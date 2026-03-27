from pathlib import Path

import joblib
import pandas as pd

from src.features.window_features import featurize_window
from src.models.predict import predict_one
from src.reporting.template_report import generate_template_report


class DummyModel:
    def predict_proba(self, x):
        return [[0.3, 0.7] for _ in range(len(x))]


def test_predict_and_report(tmp_path: Path) -> None:
    sample = pd.DataFrame({"attacker_X": [1.0, 2.0], "attacker_yaw_delta": [0.1, 0.2]})
    parquet_path = tmp_path / "sample.parquet"
    sample.to_parquet(parquet_path)

    feature_columns = list(featurize_window(sample).keys())
    bundle = {
        "pipeline": DummyModel(),
        "feature_columns": feature_columns,
        "threshold": 0.5,
    }

    bundle_path = tmp_path / "model.joblib"
    joblib.dump(bundle, bundle_path)
    loaded = joblib.load(bundle_path)

    pred = predict_one(parquet_path, loaded)
    explanation = {"top_features": [{"feature": "attacker_X__mean", "score": 1.0, "ratio": 1.0}]}
    report = generate_template_report(
        pred,
        explanation,
        policy_evidence=[
            {
                "title": "제3조 (비정상적 게임 이용 - 매크로/어뷰징)",
                "excerpt": "단순 반복 동작 자동화 및 시스템 악용 행위를 금지함.",
            }
        ],
        backend_detections=[
            {
                "type": "Consistent Speed Hack",
                "status": "High Probability",
                "avg": 14.7,
                "std_dev": 1.3,
            }
        ],
        llm_provider="ollama",
        llm_model="qwen3-vl:8b",
    )

    assert pred["pred_label"] == 1
    assert "안티치트 분석 보고서 (표준 양식 v1)" in report
    assert "정책 근거 (RAG)" in report
    assert "백엔드 핵 탐지" in report
    assert "LLM Model: qwen3-vl:8b" in report
