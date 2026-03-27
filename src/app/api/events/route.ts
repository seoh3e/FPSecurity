import { NextResponse } from "next/server";

export async function GET() {
  const data = [
    {
      id: "evt-001",
      type: "Wall Hack",
      playerId: "1023",
      riskScore: 95,
      riskLevel: "High",
      detectedAt: "2026-03-27 11:42",
    },
    {
      id: "evt-002",
      type: "Fire Rate",
      playerId: "884",
      riskScore: 61,
      riskLevel: "Medium",
      detectedAt: "2026-02-09 11:38",
    },
    {
      id: "evt-003",
      type: "Teleport Suspected",
      playerId: "155",
      riskScore: 45,
      riskLevel: "Low",
      detectedAt: "2026-02-09 11:21",
    },
    {
      id: "evt-004",
      type: "Aimbot",
      playerId: "777",
      riskScore: 88,
      riskLevel: "High",
      detectedAt: "2026-03-27 12:00",
    },
  ];

  return NextResponse.json(data);
}