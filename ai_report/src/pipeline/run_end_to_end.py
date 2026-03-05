from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from time import perf_counter

import yaml

from src.models.predict import load_bundle, predict_one
from src.reporting.llm_adapter import generate_llm_report
from src.reporting.policy_rag import retrieve_policy_evidence
from src.reporting.template_report import generate_template_report
from src.xai.explain import explain_prediction


def _load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _log(message: str) -> None:
    print(f"[infer] {message}", flush=True)


def run(config: dict, input_path: str | Path) -> dict:
    start = perf_counter()
    llm_provider = config["report"].get("llm_provider", "auto")
    llm_model = config["report"].get("llm_model", "gpt-4o-mini")

    _log(f"실행 시작: input={input_path}")
    _log(f"LLM 설정: provider={llm_provider}, model={llm_model}")

    _log("모델 로드 중...")
    bundle = load_bundle(config["model"]["model_path"])
    _log("모델 로드 완료")

    _log("예측 수행 중...")
    prediction = predict_one(input_path, bundle)
    _log(
        "예측 완료: "
        f"label={prediction.get('label_name')}, score={prediction.get('cheat_score'):.4f}, risk={prediction.get('risk_level')}"
    )

    explanation_error = None
    _log("XAI 설명 생성 중...")
    try:
        explanation = explain_prediction(bundle, prediction["feature_row"], top_k=config["report"].get("top_k", 8))
        _log(f"XAI 설명 생성 완료: top_features={len(explanation.get('top_features', []))}")
    except Exception as exc:
        explanation_error = str(exc)
        explanation = {
            "top_features": [],
            "method": "shap",
            "error": explanation_error,
        }
        _log(f"XAI 설명 생성 실패: {explanation_error}")

    policy_reference = config["report"].get("policy_reference", "운영 정책 제2조(비인가 프로그램 사용 - 핵/변조작 금지)")
    policy_path = config["report"].get("policy_path", "docs/rule.md")
    policy_query = (
        f"{policy_reference} "
        f"risk={prediction.get('risk_level', '')} "
        f"label={prediction.get('label_name', '')} "
        f"top_features={' '.join(item.get('feature', '') for item in explanation.get('top_features', []))}"
    )
    policy_error = None
    _log("정책 RAG 검색 중...")
    try:
        policy_evidence = retrieve_policy_evidence(
            policy_path=policy_path,
            query=policy_query,
            top_k=int(config["report"].get("policy_top_k", 3)),
            persist_dir=config["report"].get("policy_chroma_dir", "artifacts/chroma_policy_db"),
            collection_name=config["report"].get("policy_chroma_collection", "policy_rules"),
        )
        _log(f"정책 RAG 검색 완료: evidence={len(policy_evidence)}")
    except Exception as exc:
        policy_error = str(exc)
        policy_evidence = []
        _log(f"정책 RAG 검색 실패: {policy_error}")

    _log("템플릿 보고서 생성 중...")
    template_report = generate_template_report(
        prediction=prediction,
        explanation=explanation,
        policy_reference=policy_reference,
        policy_evidence=policy_evidence,
        llm_provider=llm_provider,
        llm_model=llm_model,
    )

    if explanation_error:
        template_report += (
            "\n\n## 설명 생성 오류\n"
            "SHAP 설명 생성에 실패했습니다. 아래 오류를 확인하세요.\n"
            f"- error: {explanation_error}\n"
        )

    if policy_error:
        template_report += (
            "\n\n## 정책 RAG 오류\n"
            "정책 벡터 검색(ChromaDB) 중 오류가 발생했습니다.\n"
            f"- error: {policy_error}\n"
        )

    _log("LLM 요약 생성 중...")
    llm_prompt = (
        "다음 분석 결과를 운영자용으로 요약하되, 반드시 아래 3개 항목만 같은 순서로 출력해.\n"
        "절대 질문형 문장, 대화체, 독자에게 묻는 표현(예: 추가 질문이 있으신가요)을 쓰지 마.\n"
        "친절 멘트/인사말/마무리 질문 없이 보고서 문체로 단정형 문장만 작성해.\n"
        "금지 표현: 물음표(?, ？), '추가 질문', '궁금한 점', '원하시면', '알려 주세요', '문의해 주세요'.\n"
        "출력은 반드시 정확히 3줄, 각 줄은 아래 접두사로 시작해야 함.\n"
        "형식:\n"
        "- 한줄 결론: ...\n"
        "- 핵심 근거 2개: 1) ... / 2) ...\n"
        "- 권고 액션: ...\n\n"
        f"예측: {json.dumps(prediction, ensure_ascii=False)}\n"
        f"근거: {json.dumps(explanation, ensure_ascii=False)}\n"
        f"정책: {policy_reference}.\n"
        f"정책 RAG 근거: {json.dumps(policy_evidence, ensure_ascii=False)}"
    )
    llm_report = generate_llm_report(
        llm_prompt,
        model=llm_model,
        provider=llm_provider,
        ollama_base_url=config["report"].get("ollama_base_url", "http://localhost:11434"),
        ollama_timeout_sec=int(config["report"].get("ollama_timeout_sec", 180)),
    )
    _log("LLM 요약 생성 완료")
    final_report = template_report + "\n\n## LLM 요약\n" + llm_report

    _log("리포트 파일 저장 중...")
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
                "policy_evidence": policy_evidence,
                "policy_error": policy_error,
                "explanation_error": explanation_error,
                "llm_used": True,
                "llm_provider": llm_provider,
                "llm_model": llm_model,
                "report_path": str(report_md),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    elapsed = perf_counter() - start
    _log(f"저장 완료: md={report_md}, json={report_json}")
    _log(f"실행 종료 (elapsed={elapsed:.2f}s)")

    return {
        "report_md": str(report_md),
        "report_json": str(report_json),
        "prediction": prediction,
        "policy_evidence": policy_evidence,
        "policy_error": policy_error,
        "explanation_error": explanation_error,
        "llm_used": True,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
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
