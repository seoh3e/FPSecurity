from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.features.window_features import featurize_window


def _risk_level(score: float, threshold: float) -> str:
    if score >= max(0.85, threshold + 0.2):
        return "HIGH"
    if score >= threshold:
        return "MEDIUM"
    return "LOW"


def load_bundle(model_path: str | Path) -> dict:
    return joblib.load(model_path)


def predict_one(parquet_path: str | Path, bundle: dict) -> dict:
    df = pd.read_parquet(parquet_path)
    row = featurize_window(df)
    x = pd.DataFrame([row])

    feature_columns: list[str] = bundle["feature_columns"]
    x_aligned = x.reindex(columns=feature_columns, fill_value=0.0)

    model = bundle["pipeline"]
    threshold = float(bundle["threshold"])
    proba = np.asarray(model.predict_proba(x_aligned), dtype=float)
    score = float(proba[:, 1][0])
    pred = int(score >= threshold)

    return {
        "input_path": str(parquet_path),
        "cheat_score": score,
        "pred_label": pred,
        "label_name": "cheater" if pred == 1 else "not_cheater",
        "threshold": threshold,
        "risk_level": _risk_level(score, threshold),
        "feature_row": row,
    }
