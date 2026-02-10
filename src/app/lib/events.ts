// src/app/lib/events.ts
import type { SecurityEvent } from "../types/events";

// 지금은 MOCK. 나중에 여기만 fetch로 바꾸면 됨.
const MOCK_EVENTS: SecurityEvent[] = [
  {
    id: "evt-001",
    type: "Speed Hack",
    playerId: "1023",
    riskScore: 82,
    riskLevel: "High",
    detectedAt: "2026-02-09 11:42",
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
];

// ✅ 이 함수만 나중에 API로 교체하면 됨
export async function getEvents(): Promise<SecurityEvent[]> {
  // TODO (backend 연결 시):
  // const res = await fetch("/api/events");
  // if (!res.ok) throw new Error("Failed to fetch events");
  // return res.json();

  // 프론트 개발 편의용: 약간의 지연을 흉내낼 수도 있음
  // await new Promise((r) => setTimeout(r, 300));

  return MOCK_EVENTS;
}
