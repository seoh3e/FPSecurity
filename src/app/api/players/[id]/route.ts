import { NextResponse } from "next/server";

export async function GET(
  req: Request,
  { params }: { params: { id: string } }
) {
  const { id } = params;

  const data = {
    playerId: id,
    recentFindings: [
      { title: "Speed Hack 의심", score: 82 },
      { title: "Fire Rate 이상", score: 61 },
    ],
    ruleDetections: [
      "이동 속도 평균 대비 2.8배 초과",
      "가속 아이템/버프 사용 기록 없음",
      "동일 세션에서 5회 반복 감지",
      "지형 상 이동 불가능 구간 포함",
    ],
    aiAnalysis: {
      narrative:
        "이동 속도가 평균 대비 2.8배이며, 가속 아이템 사용 기록이 없습니다. 반복 패턴이 확인되어 Speed Hack 가능성이 높습니다.",
      confidence: 0.92,
      recommendation: "관찰 등록 후 반복 시 제재 권고",
    },
  };

  return NextResponse.json(data);
}