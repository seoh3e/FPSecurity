from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def explain_prediction(bundle: dict, feature_row: dict[str, float], top_k: int = 8) -> dict[str, Any]:
    model = bundle["pipeline"]
    preprocessor = model.named_steps.get("preprocessor")
    classifier = model.named_steps["classifier"]
    columns: list[str] = bundle["feature_columns"]
    x_df = pd.DataFrame([feature_row]).reindex(columns=columns, fill_value=0.0)

    try:
        import shap

        x_transformed = preprocessor.transform(x_df) if preprocessor is not None else x_df.values
        explainer = shap.Explainer(classifier)
        shap_values = explainer(x_transformed)

        raw_values = shap_values.values
        if raw_values.ndim == 3:
            class_index = 1 if raw_values.shape[2] > 1 else 0
            contrib = np.abs(raw_values[0, :, class_index])
        else:
            contrib = np.abs(raw_values[0])
    except Exception as exc:
        raise RuntimeError(
            "SHAP explanation failed. This project is configured to require SHAP-only explanations."
        ) from exc

    importances = list(zip(columns, [float(v) for v in contrib]))

    importances.sort(key=lambda x: x[1], reverse=True)
    top = importances[:top_k]
    total = sum(v for _, v in top) or 1.0
    top_norm = [{"feature": k, "score": v, "ratio": v / total} for k, v in top]

    return {
        "top_features": top_norm,
        "method": "shap",
    }
