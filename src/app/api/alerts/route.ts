import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json([
    {
      id: 1,
      player_id: "p1",
      type: "Speed Hack",
      severity: "high",
      message: "이동 속도 평균 대비 2.8배 초과",
      created_at: "2026-03-28T12:00:00Z",
    },
    {
      id: 2,
      player_id: "p2",
      type: "Fire Rate",
      severity: "medium",
      message: "발사 속도 비정상 패턴 감지",
      created_at: "2026-03-28T12:10:00Z",
    },
  ]);
}