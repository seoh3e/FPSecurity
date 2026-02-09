"use client";

import { useParams } from "next/navigation";
import RiskBadge from "@/app/components/RiskBadge";

export default function PlayerPage() {
  const params = useParams();
  const idRaw = params?.id;
  const playerId = Array.isArray(idRaw) ? idRaw[0] : idRaw;

  // 예시 데이터 (나중에 백엔드 연동 시 여기만 갈아끼우면 됨)
  const recentFindings = [
    { title: "Speed Hack 의심", score: 82 },
    { title: "Fire Rate 이상", score: 61 },
  ];

  const ruleDetections = [
    "이동 속도 평균 대비 2.8배 초과",
    "가속 아이템/버프 사용 기록 없음",
    "동일 세션에서 5회 반복 감지",
    "지형 상 이동 불가능 구간 포함",
  ];

  const aiAnalysis = {
    narrative:
      "이동 속도가 평균 대비 2.8배이며, 가속 아이템 사용 기록이 없습니다. 동일 패턴이 반복되고 불가능 구간 이동이 포함되어 Speed Hack 가능성이 높습니다.",
    confidence: 0.92,
    recommendation: "관찰 등록 후, 반복 시 임시 제한(시뮬레이션) 권고",
  };

  return (
    <main style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <header style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
        <h1 style={{ margin: 0 }}>Player Detail</h1>
        <span style={{ color: "#6b7280" }}>Player ID: {playerId ?? "(없음)"}</span>
      </header>

      <section style={{ marginTop: 16 }}>
        <h2 style={{ marginBottom: 8 }}>최근 탐지 이벤트</h2>
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          {recentFindings.map((f) => (
            <li key={f.title} style={{ marginBottom: 6 }}>
              {f.title}
              <RiskBadge score={f.score} />
            </li>
          ))}
        </ul>
      </section>

      {/* 카드 2개 분리 */}
      <section
        style={{
          marginTop: 16,
          display: "grid",
          gridTemplateColumns: "1fr",
          gap: 12,
        }}
      >
        {/* Rule Detection 카드 */}
        <div style={cardStyle}>
          <div style={cardHeaderStyle}>
            <h2 style={{ margin: 0 }}>Rule Detection</h2>
            <span style={pillStyle}>증거/근거</span>
          </div>
          <p style={mutedStyle}>
            룰 기반 탐지 엔진이 트리거한 항목(정량/정적 기준)
          </p>
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {ruleDetections.map((x) => (
              <li key={x} style={{ marginBottom: 6 }}>
                {x}
              </li>
            ))}
          </ul>
        </div>

        {/* AI Analysis 카드 */}
        <div style={cardStyle}>
          <div style={cardHeaderStyle}>
            <h2 style={{ margin: 0 }}>AI Analysis</h2>
            <span style={pillStyle}>해석/판단</span>
          </div>
          <p style={mutedStyle}>
            탐지 결과를 바탕으로 맥락(반복성/패턴/상황)을 포함해 해석
          </p>

          <div style={{ lineHeight: 1.6 }}>
            <p style={{ marginTop: 0 }}>{aiAnalysis.narrative}</p>

            <p style={{ margin: "8px 0" }}>
              Confidence: <b>{aiAnalysis.confidence}</b>
            </p>

            <p style={{ marginBottom: 0 }}>
              운영 조치 권고: <b>{aiAnalysis.recommendation}</b>
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}

/* 간단 스타일 */
const cardStyle: React.CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  padding: 16,
  background: "white",
};

const cardHeaderStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 12,
  marginBottom: 6,
};

const pillStyle: React.CSSProperties = {
  fontSize: 12,
  padding: "4px 10px",
  borderRadius: 999,
  border: "1px solid #e5e7eb",
  color: "#374151",
  background: "#f9fafb",
  whiteSpace: "nowrap",
};

const mutedStyle: React.CSSProperties = {
  marginTop: 0,
  marginBottom: 10,
  color: "#6b7280",
  fontSize: 13,
};
