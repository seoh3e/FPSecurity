from __future__ import annotations

import math

import numpy as np
import pandas as pd


def _safe_float(value: float | int | np.number) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (float, int, np.number)):
        if math.isnan(float(value)):
            return 0.0
        return float(value)
    return 0.0


def featurize_window(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {"row_count": 0.0}

    numeric_df = df.select_dtypes(include=[np.number]).copy()
    feature_map: dict[str, float] = {"row_count": float(len(df))}

    if numeric_df.empty:
        return feature_map

    for col in numeric_df.columns:
        series = numeric_df[col].astype(float)
        feature_map[f"{col}__mean"] = _safe_float(series.mean())
        feature_map[f"{col}__std"] = _safe_float(series.std(ddof=0))
        feature_map[f"{col}__min"] = _safe_float(series.min())
        feature_map[f"{col}__max"] = _safe_float(series.max())
        feature_map[f"{col}__last"] = _safe_float(series.iloc[-1])
        feature_map[f"{col}__delta"] = _safe_float(series.iloc[-1] - series.iloc[0])

    return feature_map
