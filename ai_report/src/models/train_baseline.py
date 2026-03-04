from __future__ import annotations

import argparse
import json
from pathlib import Path

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


def _build_model(model_name: str, random_state: int) -> object:
    if model_name == "random_forest":
        return RandomForestClassifier(
            n_estimators=200,
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


def train(config: dict) -> dict:
    records = collect_samples(
        data_dir=config["data"]["data_dir"],
        max_per_class=config["data"].get("max_per_class"),
        seed=config["data"].get("seed", 42),
    )
    x, y, _ = build_feature_table(records)

    x_train, x_valid, y_train, y_valid = train_test_split(
        x,
        y,
        test_size=config["train"].get("valid_size", 0.2),
        random_state=config["train"].get("random_state", 42),
        stratify=y,
    )

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

    clf = _build_model(config["train"].get("model", "logistic_regression"), config["train"].get("random_state", 42))
    model = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", clf)])
    model.fit(x_train, y_train)

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

    out_dir = Path(config["output"].get("artifact_dir", "artifacts"))
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = out_dir / "model.joblib"
    meta_path = out_dir / "model_meta.json"

    bundle = {
        "pipeline": model,
        "feature_columns": list(x.columns),
        "threshold": threshold,
        "model_name": config["train"].get("model", "logistic_regression"),
    }

    joblib.dump(bundle, model_path)
    meta_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
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
