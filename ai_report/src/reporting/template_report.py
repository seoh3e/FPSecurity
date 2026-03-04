from __future__ import annotations

from datetime import datetime


def _format_top_features_table(top_features: list[dict]) -> str:
    if not top_features:
        return "| 순위 | 피처 | 중요도 | 기여율 |\n|---:|---|---:|---:|\n| 1 | N/A | 0.0000 | 0.0% |"

    lines = ["| 순위 | 피처 | 중요도 | 기여율 |", "|---:|---|---:|---:|"]
    for idx, item in enumerate(top_features, start=1):
        fname = item["feature"]
        score = item["score"]
        ratio = item["ratio"] * 100
        lines.append(f"| {idx} | {fname} | {score:.4f} | {ratio:.1f}% |")
    return "\n".join(lines)


def generate_template_report(
    prediction: dict,
    explanation: dict,
    policy_reference: str = "운영 정책 제3조(비정상 조작 금지)",
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    score = prediction["cheat_score"]
    threshold = prediction["threshold"]
    risk = prediction["risk_level"]
    label_name = prediction["label_name"]
    top_features_text = _format_top_features_table(explanation.get("top_features", []))
    explain_method = explanation.get("method", "unknown")

    recommendation = "수동 검토 권장"
    if risk == "HIGH":
        recommendation = "즉시 검토 및 임시 제재 권고"
    elif risk == "MEDIUM":
        recommendation = "우선 검토 대상 등록"

    return (
        f"# 안티치트 분석 보고서 (표준 양식 v1)\n\n"
        f"## 1) 실행 정보\n"
        f"- 생성 시각: {now}\n"
        f"- 입력 데이터: {prediction['input_path']}\n"
        f"- 정책 기준: {policy_reference}\n\n"
        f"## 2) 판정 요약\n"
        f"| 항목 | 값 |\n"
        f"|---|---|\n"
        f"| 예측 라벨 | {label_name} |\n"
        f"| 치트 점수 | {score:.4f} |\n"
        f"| 임계값 | {threshold:.4f} |\n"
        f"| 위험 등급 | {risk} |\n"
        f"| 권고 조치 | {recommendation} |\n\n"
        f"## 3) 설명 근거 (XAI)\n"
        f"- 설명 방법: {explain_method}\n"
        f"- 상위 피처 기여도:\n\n"
        f"{top_features_text}\n\n"
        f"## 4) 운영자 체크리스트\n"
        f"- [ ] 최근 3판 리플레이에서 조준/반응 패턴 재확인\n"
        f"- [ ] 유사 신고/제재 이력 확인\n"
        f"- [ ] 정책 조항 적합성 검토 후 제재 수위 확정\n\n"
        f"## 5) 면책 및 주의\n"
        f"본 결과는 AI 보조 판단입니다. 최종 제재는 운영자가 매치 리플레이/로그를 재검토 후 확정하세요.\n"
    )
