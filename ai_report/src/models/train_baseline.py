from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_recall_curve, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight

from src.data.load_parquet import build_feature_table, collect_samples


def _load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _pick_threshold(y_true: pd.Series, y_score: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, y_score)
    best_f1 = -1.0
    best_threshold = 0.5
    for idx, threshold in enumerate(thresholds):
        p = precision[idx]
        r = recall[idx]
        if p + r == 0:
            continue
        f1 = 2 * p * r / (p + r)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = float(threshold)
    return best_threshold


def _build_model(model_name: str, random_state: int, n_estimators: int) -> object:
    if model_name == "random_forest":
        return RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=None,
            n_jobs=-1,
            random_state=random_state,
            class_weight="balanced",
        )
    return LogisticRegression(
        max_iter=1000,
        n_jobs=1,
        random_state=random_state,
        class_weight="balanced",
    )


def _log(message: str) -> None:
    print(f"[train] {message}", flush=True)


def _inline_progress(prefix: str, current: int, total: int) -> None:
    if total <= 0:
        return
    line = f"[train] {prefix}: {current}/{total}"
    if sys.stdout.isatty():
        print(f"\r{line}", end="", flush=True)
        if current >= total:
            print("", flush=True)
    else:
        if current == 0 or current >= total:
            _log(f"{prefix}: {current}/{total}")


def _fit_model_with_progress(
    model_name: str,
    preprocessor: ColumnTransformer,
    classifier: object,
    x_train: pd.DataFrame,
    y_train: pd.Series,
) -> Pipeline:
    model = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", classifier)])

    if model_name != "random_forest":
        _log("모델 학습 중...")
        model.fit(x_train, y_train)
        _log("모델 학습 완료")
        return model

    _log("모델 학습 중... (tree progress)")
    x_train_processed = preprocessor.fit_transform(x_train)
    total_trees = int(classifier.n_estimators)

    if classifier.class_weight in {"balanced", "balanced_subsample"}:
        classes = np.unique(y_train)
        class_weights = compute_class_weight(class_weight="balanced", classes=classes, y=np.asarray(y_train))
        classifier.set_params(class_weight={int(cls): float(w) for cls, w in zip(classes, class_weights)})

    classifier.set_params(warm_start=True)
    _inline_progress("모델 학습 진행", 0, total_trees)

    for tree_idx in range(1, total_trees + 1):
        classifier.set_params(n_estimators=tree_idx)
        classifier.fit(x_train_processed, y_train)
        _inline_progress("모델 학습 진행", tree_idx, total_trees)

    _log("모델 학습 완료")
    return model


def train(config: dict) -> dict:
    train_start = perf_counter()
    _log("학습 시작")

    data_dir = config["data"]["data_dir"]
    max_per_class = config["data"].get("max_per_class")
    data_seed = config["data"].get("seed", 42)
    _log(f"샘플 수집 중... data_dir={data_dir}, max_per_class={max_per_class}, seed={data_seed}")
    records = collect_samples(
        data_dir=data_dir,
        max_per_class=max_per_class,
        seed=data_seed,
    )
    _log(f"샘플 수집 완료: {len(records)}건")

    feature_progress_every = int(config["train"].get("feature_progress_every", 50))
    _log(f"피처 테이블 생성 중... (progress every {feature_progress_every})")

    def on_feature_progress(current: int, total: int) -> None:
        _inline_progress("피처 생성 진행", current, total)

    x, y, _ = build_feature_table(
        records,
        progress_callback=on_feature_progress,
        progress_every=feature_progress_every,
    )
    _log(f"피처 생성 완료: samples={len(x)}, features={x.shape[1]}")

    valid_size = config["train"].get("valid_size", 0.2)
    random_state = config["train"].get("random_state", 42)
    _log(f"데이터 분할 중... valid_size={valid_size}, random_state={random_state}")
    x_train, x_valid, y_train, y_valid = train_test_split(
        x,
        y,
        test_size=valid_size,
        random_state=random_state,
        stratify=y,
    )
    _log(f"분할 완료: train={len(x_train)}, valid={len(x_valid)}")

    numeric_cols = list(x_train.columns)
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_cols,
            )
        ],
        remainder="drop",
    )

    model_name = config["train"].get("model", "logistic_regression")
    n_estimators = int(config["train"].get("n_estimators", 200))
    _log(f"모델 초기화: {model_name}")
    clf = _build_model(model_name, random_state, n_estimators)
    model = _fit_model_with_progress(model_name, preprocessor, clf, x_train, y_train)

    _log("검증 및 임계값 탐색 중...")
    valid_score = model.predict_proba(x_valid)[:, 1]
    threshold = _pick_threshold(y_valid, valid_score)
    valid_pred = (valid_score >= threshold).astype(int)

    metrics = {
        "f1": float(f1_score(y_valid, valid_pred)),
        "auroc": float(roc_auc_score(y_valid, valid_score)),
        "threshold": float(threshold),
        "num_samples": int(len(x)),
        "num_features": int(x.shape[1]),
    }
    _log(
        "검증 완료: "
        f"f1={metrics['f1']:.4f}, auroc={metrics['auroc']:.4f}, threshold={metrics['threshold']:.4f}"
    )

    out_dir = Path(config["output"].get("artifact_dir", "artifacts"))
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "model.joblib"
    meta_path = out_dir / "model_meta.json"

    bundle = {
        "pipeline": model,
        "feature_columns": list(x.columns),
        "threshold": threshold,
        "model_name": model_name,
    }

    _log("산출물 저장 중...")
    joblib.dump(bundle, model_path)
    meta_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    elapsed_sec = perf_counter() - train_start
    _log(f"저장 완료: model={model_path}, meta={meta_path}")
    _log(f"학습 종료 (elapsed={elapsed_sec:.2f}s)")
    return {"model_path": str(model_path), "meta_path": str(meta_path), "metrics": metrics}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train baseline anti-cheat classifier")
    parser.add_argument("--config", default="configs/train.yaml", help="Path to training config")
    args = parser.parse_args()

    config = _load_yaml(args.config)
    result = train(config)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
