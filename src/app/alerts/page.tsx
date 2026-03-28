import Link from "next/link";

type Violation = {
  type?: string;
  avg?: number;
  std_dev?: number;
  status?: string;
  [key: string]: unknown;
};

type AlertPayload = {
  player_id?: string;
  session_id?: string;
  violations?: Violation[];
  timestamp?: string;
  [key: string]: unknown;
};

type AlertItem = {
  id: number;
  player_id: string;
  session_id: string;
  created_at: string;
  alert?: AlertPayload;
};

type AlertsResponse = {
  total: number;
  limit: number;
  offset: number;
  items: AlertItem[];
};

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getRiskLevel(type?: string) {
  if (!type) return "Low";

  if (
    type.includes("Speed Hack") ||
    type.includes("Damage Hack") ||
    type.includes("Aimbot")
  ) {
    return "High";
  }

  if (
    type.includes("Rapid Fire") ||
    type.includes("Unauthorized") ||
    type.includes("DDoS")
  ) {
    return "Medium";
  }

  return "Low";
}

function getRiskScore(type?: string) {
  const level = getRiskLevel(type);
  if (level === "High") return 3;
  if (level === "Medium") return 2;
  return 1;
}

function badgeStyle(level: string): React.CSSProperties {
  if (level === "High") {
    return {
      display: "inline-block",
      padding: "4px 10px",
      borderRadius: 999,
      fontSize: 12,
      fontWeight: 700,
      backgroundColor: "#fee2e2",
      color: "#b91c1c",
      border: "1px solid #fecaca",
    };
  }

  if (level === "Medium") {
    return {
      display: "inline-block",
      padding: "4px 10px",
      borderRadius: 999,
      fontSize: 12,
      fontWeight: 700,
      backgroundColor: "#ffedd5",
      color: "#c2410c",
      border: "1px solid #fdba74",
    };
  }

  return {
    display: "inline-block",
    padding: "4px 10px",
    borderRadius: 999,
    fontSize: 12,
    fontWeight: 700,
    backgroundColor: "#f3f4f6",
    color: "#374151",
    border: "1px solid #d1d5db",
  };
}

export default async function AlertsPage() {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
  const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

  const res = await fetch(
    `${API_BASE_URL}/api/v1/alerts?limit=50&offset=0`,
    {
      headers: {
        "X-API-Key": API_KEY ?? "",
      },
      cache: "no-store",
    }
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to fetch alerts: ${res.status} ${text}`);
  }

  const data: AlertsResponse = await res.json();

  const sortedItems = [...data.items].sort((a, b) => {
    const aType = a.alert?.violations?.[0]?.type;
    const bType = b.alert?.violations?.[0]?.type;

    const scoreDiff = getRiskScore(bType) - getRiskScore(aType);
    if (scoreDiff !== 0) return scoreDiff;

    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  const highCount = sortedItems.filter(
    (item) => getRiskLevel(item.alert?.violations?.[0]?.type) === "High"
  ).length;

  const mediumCount = sortedItems.filter(
    (item) => getRiskLevel(item.alert?.violations?.[0]?.type) === "Medium"
  ).length;

  const latestDetectedAt =
    sortedItems.length > 0 ? formatDate(sortedItems[0].created_at) : "-";

  return (
    <main style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 28 }}>보안 알림 대시보드</h1>
        <p style={{ marginTop: 8, color: "#6b7280" }}>
          탐지된 이상행동 알림을 우선순위 중심으로 확인합니다.
        </p>
      </div>

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 12,
          marginBottom: 24,
        }}
      >
        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>전체 알림 수</div>
          <div style={summaryValueStyle}>{data.total}</div>
        </div>

        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>High 위험</div>
          <div style={{ ...summaryValueStyle, color: "#b91c1c" }}>
            {highCount}
          </div>
        </div>

        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>Medium 위험</div>
          <div style={{ ...summaryValueStyle, color: "#c2410c" }}>
            {mediumCount}
          </div>
        </div>

        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>최근 탐지 시간</div>
          <div style={{ ...summaryValueStyle, fontSize: 18 }}>
            {latestDetectedAt}
          </div>
        </div>
      </section>

      <section style={{ display: "grid", gap: 14 }}>
        {sortedItems.length === 0 ? (
          <div style={emptyStateStyle}>현재 표시할 알림이 없습니다.</div>
        ) : (
          sortedItems.map((item) => {
            const violation = item.alert?.violations?.[0];
            const type = violation?.type ?? "Unknown";
            const riskLevel = getRiskLevel(type);

            return (
              <article key={item.id} style={cardStyle}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: 12,
                    flexWrap: "wrap",
                  }}
                >
                  <div>
                    <div style={{ marginBottom: 8 }}>
                      <span style={badgeStyle(riskLevel)}>{riskLevel}</span>
                    </div>
                    <h2 style={{ margin: 0, fontSize: 20 }}>{type}</h2>
                    <p style={{ marginTop: 8, marginBottom: 0, color: "#6b7280" }}>
                      탐지 시간: {formatDate(item.created_at)}
                    </p>
                  </div>

                  <div
                    style={{
                      minWidth: 220,
                      background: "#f9fafb",
                      border: "1px solid #e5e7eb",
                      borderRadius: 12,
                      padding: 12,
                    }}
                  >
                    <div style={metaRowStyle}>
                      <span style={metaLabelStyle}>Player ID</span>
                      <Link
                        href={`/players/${item.player_id}`}
                        style={{ textDecoration: "none" }}
                      >
                        <span
                          style={{
                            ...metaValueStyle,
                            color: "#2563eb",
                            cursor: "pointer",
                            textDecoration: "underline",
                          }}
                        >
                          {item.player_id}
                        </span>
                      </Link>
                    </div>

                    <div style={metaRowStyle}>
                      <span style={metaLabelStyle}>Session ID</span>
                      <span style={metaValueStyle}>{item.session_id}</span>
                    </div>

                    {violation?.status && (
                      <div style={metaRowStyle}>
                        <span style={metaLabelStyle}>판정</span>
                        <span style={metaValueStyle}>
                          {String(violation.status)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div
                  style={{
                    marginTop: 16,
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                    gap: 10,
                  }}
                >
                  {typeof violation?.avg === "number" && (
                    <div style={infoBoxStyle}>
                      <div style={infoLabelStyle}>평균값</div>
                      <div style={infoValueStyle}>{violation.avg}</div>
                    </div>
                  )}

                  {typeof violation?.std_dev === "number" && (
                    <div style={infoBoxStyle}>
                      <div style={infoLabelStyle}>표준편차</div>
                      <div style={infoValueStyle}>{violation.std_dev}</div>
                    </div>
                  )}
                </div>

                <details style={{ marginTop: 16 }}>
                  <summary style={detailsSummaryStyle}>상세 JSON 보기</summary>
                  <pre style={preStyle}>
                    {JSON.stringify(item, null, 2)}
                  </pre>
                </details>
              </article>
            );
          })
        )}
      </section>
    </main>
  );
}

const summaryCardStyle: React.CSSProperties = {
  background: "white",
  border: "1px solid #e5e7eb",
  borderRadius: 16,
  padding: 18,
  boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
};

const summaryLabelStyle: React.CSSProperties = {
  fontSize: 13,
  color: "#6b7280",
  marginBottom: 8,
};

const summaryValueStyle: React.CSSProperties = {
  fontSize: 28,
  fontWeight: 800,
  color: "#111827",
};

const emptyStateStyle: React.CSSProperties = {
  padding: 24,
  borderRadius: 16,
  border: "1px dashed #d1d5db",
  backgroundColor: "#f9fafb",
  color: "#6b7280",
};

const cardStyle: React.CSSProperties = {
  background: "white",
  border: "1px solid #e5e7eb",
  borderRadius: 18,
  padding: 20,
  boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
};

const metaRowStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 12,
  marginBottom: 8,
};

const metaLabelStyle: React.CSSProperties = {
  color: "#6b7280",
  fontSize: 13,
};

const metaValueStyle: React.CSSProperties = {
  color: "#111827",
  fontWeight: 600,
  fontSize: 13,
};

const infoBoxStyle: React.CSSProperties = {
  background: "#f9fafb",
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  padding: 14,
};

const infoLabelStyle: React.CSSProperties = {
  color: "#6b7280",
  fontSize: 12,
  marginBottom: 6,
};

const infoValueStyle: React.CSSProperties = {
  color: "#111827",
  fontWeight: 700,
  fontSize: 20,
};

const detailsSummaryStyle: React.CSSProperties = {
  cursor: "pointer",
  fontWeight: 600,
  color: "#374151",
};

const preStyle: React.CSSProperties = {
  whiteSpace: "pre-wrap",
  marginTop: 12,
  background: "#111827",
  color: "#f9fafb",
  padding: 16,
  borderRadius: 12,
  overflowX: "auto",
  fontSize: 13,
};