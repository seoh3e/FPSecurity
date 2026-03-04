from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import yaml

from src.models.predict import load_bundle, predict_one
from src.reporting.llm_adapter import generate_llm_report
from src.reporting.template_report import generate_template_report
from src.xai.explain import explain_prediction


def _load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(config: dict, input_path: str | Path) -> dict:
    bundle = load_bundle(config["model"]["model_path"])
    prediction = predict_one(input_path, bundle)
    explanation_error = None
    try:
        explanation = explain_prediction(bundle, prediction["feature_row"], top_k=config["report"].get("top_k", 8))
    except Exception as exc:
        explanation_error = str(exc)
        explanation = {
            "top_features": [],
            "method": "shap",
            "error": explanation_error,
        }

    template_report = generate_template_report(
        prediction=prediction,
        explanation=explanation,
        policy_reference=config["report"].get("policy_reference", "운영 정책 제3조(비정상 조작 금지)"),
    )

    if explanation_error:
        template_report += (
            "\n\n## 설명 생성 오류\n"
            "SHAP 설명 생성에 실패했습니다. 아래 오류를 확인하세요.\n"
            f"- error: {explanation_error}\n"
        )

    llm_prompt = (
        "다음 분석 결과를 운영자용으로 요약하되, 반드시 아래 3개 항목만 같은 순서로 출력해.\n"
        "형식:\n"
        "- 한줄 결론: ...\n"
        "- 핵심 근거 2개: 1) ... / 2) ...\n"
        "- 권고 액션: ...\n\n"
        f"예측: {json.dumps(prediction, ensure_ascii=False)}\n"
        f"근거: {json.dumps(explanation, ensure_ascii=False)}\n"
        "정책: 운영 정책 제3조(비정상 조작 금지)."
    )
    llm_report = generate_llm_report(
        llm_prompt,
        model=config["report"].get("llm_model", "gpt-4o-mini"),
        provider=config["report"].get("llm_provider", "auto"),
        ollama_base_url=config["report"].get("ollama_base_url", "http://localhost:11434"),
        ollama_timeout_sec=int(config["report"].get("ollama_timeout_sec", 180)),
    )
    final_report = template_report + "\n\n## LLM 요약\n" + llm_report

    out_dir = Path(config["output"].get("report_dir", "artifacts/reports"))
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_md = out_dir / f"report_{ts}.md"
    report_json = out_dir / f"report_{ts}.json"

    report_md.write_text(final_report, encoding="utf-8")
    report_json.write_text(
        json.dumps(
            {
                "prediction": prediction,
                "explanation": explanation,
                "explanation_error": explanation_error,
                "llm_used": True,
                "report_path": str(report_md),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return {
        "report_md": str(report_md),
        "report_json": str(report_json),
        "prediction": prediction,
        "explanation_error": explanation_error,
        "llm_used": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run end-to-end inference + explanation + reporting")
    parser.add_argument("--config", default="configs/infer.yaml", help="Path to inference config")
    parser.add_argument("--input", required=True, help="Input parquet file path")
    args = parser.parse_args()

    config = _load_yaml(args.config)
    result = run(config=config, input_path=args.input)
    # print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
