"use client";

import Link from "next/link";
import RiskBadge from "@/app/components/RiskBadge";

type RiskLevel = "High" | "Medium" | "Low";

type EventRow = {
  id: string;            // 이벤트 ID (임시)
  type: string;          // 탐지 유형
  playerId: string;      // 플레이어 ID
  riskScore: number;     // 점수
  riskLevel: RiskLevel;  // 레벨
  detectedAt: string;    // 시간(표시용)
};

const MOCK_EVENTS: EventRow[] = [
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

// 점수 기반 정렬/필터에 쓰기 좋게 risk를 숫자로 매핑
const riskRank: Record<RiskLevel, number> = { High: 3, Medium: 2, Low: 1 };

export default function EventsPage() {
  // 지금은 목데이터지만, 나중에 여기만 fetch로 바꾸면 됨.
  const events = [...MOCK_EVENTS].sort((a, b) => {
    // 1순위: 레벨(High > Medium > Low)
    if (riskRank[b.riskLevel] !== riskRank[a.riskLevel]) {
      return riskRank[b.riskLevel] - riskRank[a.riskLevel];
    }
    // 2순위: 점수(내림차순)
    return b.riskScore - a.riskScore;
  });

  return (
    <main style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <header style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
        <h1 style={{ margin: 0 }}>Security Events</h1>
        <span style={{ opacity: 0.7 }}>관리자 탐지 이벤트 목록</span>
      </header>

      <div style={{ height: 16 }} />

      <div
        style={{
          borderRadius: 14,
          border: "1px solid rgba(255,255,255,0.08)",
          overflow: "hidden",
          background: "rgba(255,255,255,0.03)",
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: "rgba(255,255,255,0.04)" }}>
              <Th>탐지 유형</Th>
              <Th>Player</Th>
              <Th>Risk</Th>
              <Th>Detected At</Th>
              <Th style={{ textAlign: "right" }}>Action</Th>
            </tr>
          </thead>

          <tbody>
            {events.map((e) => (
              <tr
                key={e.id}
                style={{
                  borderTop: "1px solid rgba(255,255,255,0.06)",
                }}
              >
                <Td>
                  <b>{e.type}</b>
                </Td>

                <Td>
                  <Link
                    href={`/players/${e.playerId}`}
                    style={{ textDecoration: "none" }}
                  >
                    <span style={{ color: "white" }}>#{e.playerId}</span>
                  </Link>
                </Td>

                <Td>
                  <RiskBadge score={e.riskScore} />
                </Td>

                <Td style={{ opacity: 0.85 }}>{e.detectedAt}</Td>

                <Td style={{ textAlign: "right" }}>
                  <Link
                    href={`/players/${e.playerId}`}
                    style={{
                      textDecoration: "none",
                      display: "inline-block",
                      padding: "8px 12px",
                      borderRadius: 10,
                      border: "1px solid rgba(255,255,255,0.12)",
                      color: "white",
                      background: "rgba(0,0,0,0.2)",
                    }}
                  >
                    View Detail →
                  </Link>
                </Td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ height: 10 }} />
      <p style={{ opacity: 0.65, margin: 0 }}>
        * 현재는 목데이터(MOCK)이며, 이후 백엔드 API로 교체 예정
      </p>
    </main>
  );
}

function Th({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
}) {
  return (
    <th
      style={{
        textAlign: "left",
        fontWeight: 600,
        padding: "14px 14px",
        fontSize: 13,
        opacity: 0.8,
        ...style,
      }}
    >
      {children}
    </th>
  );
}

function Td({
  children,
  style,
}: {
  children: React.ReactNode;
  style?: React.CSSProperties;
}) {
  return (
    <td
      style={{
        padding: "14px 14px",
        verticalAlign: "middle",
        ...style,
      }}
    >
      {children}
    </td>
  );
}
