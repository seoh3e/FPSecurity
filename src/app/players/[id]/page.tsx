import RiskBadge from "@/app/components/RiskBadge";

type PlayerData = {
  playerId: string;
  recentFindings: { title: string; score: number }[];
  ruleDetections: string[];
  aiAnalysis: {
    narrative: string;
    confidence: number;
    recommendation: string;
  };
};

export default async function PlayerPage({
  params,
}: {
  params: { id: string };
}) {
  const res = await fetch(`http://localhost:3000/api/players/${params.id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch player data");
  }

  const data: PlayerData = await res.json();

  return (
    <main style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <header style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
        <h1 style={{ margin: 0 }}>플레이어 상세 분석</h1>
        <span style={{ color: "#9ca3af" }}>플레이어 ID: {data.playerId}</span>
      </header>

      <section style={{ marginTop: 16 }}>
        <h2 style={{ marginBottom: 8 }}>최근 탐지 이벤트</h2>
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          {data.recentFindings.map((f) => (
            <li key={f.title} style={{ marginBottom: 6 }}>
              {f.title} <RiskBadge score={f.score} />
            </li>
          ))}
        </ul>
      </section>

      <section style={{ marginTop: 16, display: "grid", gap: 12 }}>
        <div style={cardStyle}>
          <h2 style={cardTitleStyle}>규칙 기반 탐지</h2>
          <ul style={{ margin: 0, paddingLeft: 18, color: "#111827" }}>
            {data.ruleDetections.map((x) => (
              <li key={x} style={{ marginBottom: 6, color: "#111827" }}>
                {x}
              </li>
            ))}
          </ul>
        </div>

        <div style={cardStyle}>
          <h2 style={cardTitleStyle}>AI 분석</h2>
          <p style={cardTextStyle}>{data.aiAnalysis.narrative}</p>
          <p style={cardTextStyle}>
            신뢰도: <b>{data.aiAnalysis.confidence}</b>
          </p>
          <p style={cardTextStyle}>
            운영 조치 권고: <b>{data.aiAnalysis.recommendation}</b>
          </p>
        </div>
      </section>
    </main>
  );
}

const cardStyle: React.CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  padding: 16,
  background: "white",
  color: "#111827",
};

const cardTitleStyle: React.CSSProperties = {
  marginTop: 0,
  marginBottom: 12,
  color: "#111827",
};

const cardTextStyle: React.CSSProperties = {
  color: "#111827",
  lineHeight: 1.6,
  marginTop: 0,
  marginBottom: 10,
};