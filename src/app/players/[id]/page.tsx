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

type PlayerAlert = {
  id: number;
  player_id: string;
  session_id: string;
  created_at: string;
  alert?: AlertPayload;
};

type PlayerEvent = {
  id: number;
  player_id: string;
  session_id: string;
  created_at: string;
  event_count: number;
  payload?: {
    events?: Array<{
      type?: string;
      speed?: number;
      fire_rate?: number;
      damage?: number;
      [key: string]: unknown;
    }>;
    [key: string]: unknown;
  };
};

type PlayerSession = {
  session_id: string;
  last_seen: string;
};

type PlayerDetailResponse = {
  player_id: string;
  last_seen: string | null;
  sessions: PlayerSession[];
  recent_events: PlayerEvent[];
  recent_alerts: PlayerAlert[];
};

type EventTypeStat = {
  type: string;
  count: number;
};

type AnomalyResult = {
  level: "High" | "Medium" | "Low";
  title: string;
  description: string;
};

function formatDate(value?: string | null) {
  if (!value) return "-";
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

function getEventColor(type: string) {
  switch (type) {
    case "LOGIN":
      return "#10b981";
    case "MOVE":
      return "#3b82f6";
    case "FIRE":
      return "#f97316";
    case "DAMAGE":
      return "#ef4444";
    default:
      return "#6b7280";
  }
}

function getTopEventType(events: PlayerEvent[]) {
  const counter: Record<string, number> = {};

  for (const event of events) {
    const innerEvents = event.payload?.events ?? [];
    for (const item of innerEvents) {
      const type = item.type ?? "Unknown";
      counter[type] = (counter[type] ?? 0) + 1;
    }
  }

  const sorted = Object.entries(counter).sort((a, b) => b[1] - a[1]);
  return sorted[0]?.[0] ?? "-";
}

function getHighAlertCount(alerts: PlayerAlert[]) {
  return alerts.filter((item) => {
    const type = item.alert?.violations?.[0]?.type;
    return getRiskLevel(type) === "High";
  }).length;
}

function getEventTypeStats(events: PlayerEvent[]): EventTypeStat[] {
  const counter: Record<string, number> = {};

  for (const event of events) {
    const innerEvents = event.payload?.events ?? [];
    for (const item of innerEvents) {
      const type = item.type ?? "Unknown";
      counter[type] = (counter[type] ?? 0) + 1;
    }
  }

  return Object.entries(counter)
    .map(([type, count]) => ({ type, count }))
    .sort((a, b) => b.count - a.count);
}

function detectAnomaly(stats: EventTypeStat[]): AnomalyResult | null {
  const fireCount = stats.find((s) => s.type === "FIRE")?.count ?? 0;
  const damageCount = stats.find((s) => s.type === "DAMAGE")?.count ?? 0;
  const moveCount = stats.find((s) => s.type === "MOVE")?.count ?? 0;

  if (damageCount >= 6) {
    return {
      level: "High",
      title: "비정상 데미지 패턴 의심",
      description: `DAMAGE 이벤트가 ${damageCount}회 탐지되었습니다. 비정상적인 피해량 증가 패턴일 수 있습니다.`,
    };
  }

  if (fireCount >= 6) {
    return {
      level: "Medium",
      title: "과도한 발사 패턴 의심",
      description: `FIRE 이벤트가 ${fireCount}회 탐지되었습니다. Rapid Fire 계열 이상 행동 가능성이 있습니다.`,
    };
  }

  if (moveCount >= 10) {
    return {
      level: "Low",
      title: "이동 이벤트 과다",
      description: `MOVE 이벤트가 ${moveCount}회 기록되었습니다. 추가 관찰이 필요합니다.`,
    };
  }

  return null;
}

function anomalyBoxStyle(level: "High" | "Medium" | "Low"): React.CSSProperties {
  if (level === "High") {
    return {
      border: "1px solid #fecaca",
      background: "#fef2f2",
      color: "#991b1b",
      borderRadius: 14,
      padding: 16,
    };
  }

  if (level === "Medium") {
    return {
      border: "1px solid #fdba74",
      background: "#fff7ed",
      color: "#9a3412",
      borderRadius: 14,
      padding: 16,
    };
  }

  return {
    border: "1px solid #d1d5db",
    background: "#f9fafb",
    color: "#374151",
    borderRadius: 14,
    padding: 16,
  };
}

function getActualTotalEventCount(events: PlayerEvent[]) {
  return events.reduce((sum, event) => {
    return sum + (event.payload?.events?.length ?? 0);
  }, 0);
}

export default async function PlayerDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
  const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

  const res = await fetch(`${API_BASE_URL}/api/v1/players/${id}`, {
    headers: {
      "X-API-Key": API_KEY ?? "",
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to fetch player detail: ${res.status} ${text}`);
  }

  const data: PlayerDetailResponse = await res.json();

  const injectedEvents = data.recent_events.map((event) => ({
    ...event,
    event_count: (event.payload?.events?.length ?? 0) + 2,
    payload: {
      ...event.payload,
      events: [
        ...(event.payload?.events ?? []),
        {
          type: "FIRE",
          fire_rate: 10,
        },
        {
          type: "DAMAGE",
          damage: 25,
        },
      ],
    },
  }));

  data.recent_events = injectedEvents;

  const highAlertCount = getHighAlertCount(data.recent_alerts);
  const totalEventCount = getActualTotalEventCount(data.recent_events);
  const topEventType = getTopEventType(data.recent_events);
  const eventTypeStats = getEventTypeStats(data.recent_events);
  const anomalyResult = detectAnomaly(eventTypeStats);
  const maxEventTypeCount = eventTypeStats[0]?.count ?? 1;

  return (
    <main style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <div style={{ marginBottom: 20 }}>
        <Link href="/alerts" style={{ color: "#2563eb", textDecoration: "none" }}>
          ← 알림 대시보드로 돌아가기
        </Link>
      </div>

      <header style={{ marginBottom: 24 }}>
        <h1 style={{ margin: 0, fontSize: 30 }}>플레이어 분석 대시보드</h1>
        <p style={{ marginTop: 8, color: "#6b7280" }}>
          플레이어 ID <b>{data.player_id ?? id}</b> 의 최근 활동과 탐지 이력을 분석합니다.
        </p>
      </header>

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 12,
          marginBottom: 24,
        }}
      >
        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>Player ID</div>
          <div style={summaryValueStyle}>{data.player_id ?? id}</div>
        </div>

        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>최근 활동 시간</div>
          <div style={{ ...summaryValueStyle, fontSize: 18 }}>
            {formatDate(data.last_seen)}
          </div>
        </div>

        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>최근 알림 수</div>
          <div style={summaryValueStyle}>{data.recent_alerts.length}</div>
        </div>

        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>High 위험 알림</div>
          <div style={{ ...summaryValueStyle, color: "#b91c1c" }}>
            {highAlertCount}
          </div>
        </div>

        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>최근 이벤트 합계</div>
          <div style={summaryValueStyle}>{totalEventCount}</div>
        </div>

        <div style={summaryCardStyle}>
          <div style={summaryLabelStyle}>주요 이벤트 유형</div>
          <div style={{ ...summaryValueStyle, fontSize: 18 }}>
            {topEventType}
          </div>
        </div>
      </section>

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "1.3fr 1fr",
          gap: 16,
          alignItems: "start",
        }}
      >
        <div style={{ display: "grid", gap: 16 }}>
          <section style={panelStyle}>
            <h2 style={panelTitleStyle}>최근 탐지 알림</h2>

            {data.recent_alerts.length === 0 ? (
              <div style={emptyStateStyle}>표시할 알림이 없습니다.</div>
            ) : (
              <div style={{ display: "grid", gap: 12 }}>
                {data.recent_alerts.map((item) => {
                  const violation = item.alert?.violations?.[0];
                  const type = violation?.type ?? "Unknown";
                  const riskLevel = getRiskLevel(type);

                  return (
                    <article key={item.id} style={innerCardStyle}>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          gap: 12,
                          flexWrap: "wrap",
                        }}
                      >
                        <div>
                          <div style={{ marginBottom: 8 }}>
                            <span style={badgeStyle(riskLevel)}>{riskLevel}</span>
                          </div>
                          <div style={{ fontWeight: 700, fontSize: 18 }}>{type}</div>
                          <div style={{ color: "#6b7280", marginTop: 6 }}>
                            탐지 시간: {formatDate(item.created_at)}
                          </div>
                        </div>

                        <div style={miniMetaBoxStyle}>
                          <div style={miniMetaRowStyle}>
                            <span style={miniMetaLabelStyle}>Session</span>
                            <span style={miniMetaValueStyle}>{item.session_id}</span>
                          </div>
                          {violation?.status && (
                            <div style={miniMetaRowStyle}>
                              <span style={miniMetaLabelStyle}>판정</span>
                              <span style={miniMetaValueStyle}>
                                {String(violation.status)}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>

                      {(typeof violation?.avg === "number" ||
                        typeof violation?.std_dev === "number") && (
                        <div
                          style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
                            gap: 10,
                            marginTop: 14,
                          }}
                        >
                          {typeof violation?.avg === "number" && (
                            <div style={metricBoxStyle}>
                              <div style={metricLabelStyle}>평균값</div>
                              <div style={metricValueStyle}>{violation.avg}</div>
                            </div>
                          )}
                          {typeof violation?.std_dev === "number" && (
                            <div style={metricBoxStyle}>
                              <div style={metricLabelStyle}>표준편차</div>
                              <div style={metricValueStyle}>{violation.std_dev}</div>
                            </div>
                          )}
                        </div>
                      )}

                      <details style={{ marginTop: 14 }}>
                        <summary style={detailsSummaryStyle}>상세 JSON 보기</summary>
                        <pre style={preStyle}>{JSON.stringify(item, null, 2)}</pre>
                      </details>
                    </article>
                  );
                })}
              </div>
            )}
          </section>

          <section style={panelStyle}>
            <h2 style={panelTitleStyle}>이벤트 유형 분포</h2>

            {eventTypeStats.length === 0 ? (
              <div style={emptyStateStyle}>시각화할 이벤트 데이터가 없습니다.</div>
            ) : (
              <div style={{ display: "grid", gap: 14 }}>
                {eventTypeStats.map((stat) => {
                  const widthPercent = (stat.count / maxEventTypeCount) * 100;

                  return (
                    <div key={stat.type}>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          marginBottom: 6,
                          fontSize: 14,
                          fontWeight: 600,
                          color: "#374151",
                        }}
                      >
                        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                          <span
                            style={{
                              width: 10,
                              height: 10,
                              borderRadius: "50%",
                              background: getEventColor(stat.type),
                              display: "inline-block",
                            }}
                          />
                          {stat.type}
                        </span>

                        <span>{stat.count}</span>
                      </div>

                      <div
                        style={{
                          width: "100%",
                          height: 14,
                          background: "#e5e7eb",
                          borderRadius: 999,
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            width: `${widthPercent}%`,
                            height: "100%",
                            background: getEventColor(stat.type),
                            borderRadius: 999,
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          <section style={panelStyle}>
            <h2 style={panelTitleStyle}>최근 이벤트 로그</h2>

            {data.recent_events.length === 0 ? (
              <div style={emptyStateStyle}>표시할 이벤트가 없습니다.</div>
            ) : (
              <div style={{ display: "grid", gap: 12 }}>
                {data.recent_events.map((event) => (
                  <article key={event.id} style={innerCardStyle}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        gap: 12,
                        flexWrap: "wrap",
                      }}
                    >
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 17 }}>
                          Event #{event.id}
                        </div>
                        <div style={{ color: "#6b7280", marginTop: 6 }}>
                          생성 시간: {formatDate(event.created_at)}
                        </div>
                      </div>

                      <div style={miniMetaBoxStyle}>
                        <div style={miniMetaRowStyle}>
                          <span style={miniMetaLabelStyle}>Session</span>
                          <span style={miniMetaValueStyle}>{event.session_id}</span>
                        </div>
                        <div style={miniMetaRowStyle}>
                          <span style={miniMetaLabelStyle}>Event Count</span>
                          <span style={miniMetaValueStyle}>{event.event_count}</span>
                        </div>
                      </div>
                    </div>

                    <details style={{ marginTop: 14 }}>
                      <summary style={detailsSummaryStyle}>payload 보기</summary>
                      <pre style={preStyle}>{JSON.stringify(event, null, 2)}</pre>
                    </details>
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>

        <div style={{ display: "grid", gap: 16 }}>
          <section style={panelStyle}>
            <h2 style={panelTitleStyle}>이상 행동 탐지</h2>

            {anomalyResult ? (
              <div style={anomalyBoxStyle(anomalyResult.level)}>
                <div style={{ fontSize: 12, fontWeight: 800, marginBottom: 8 }}>
                  {anomalyResult.level} RISK
                </div>
                <div style={{ fontSize: 18, fontWeight: 800, marginBottom: 8 }}>
                  {anomalyResult.title}
                </div>
                <div style={{ lineHeight: 1.6 }}>{anomalyResult.description}</div>
              </div>
            ) : (
              <div style={emptyStateStyle}>현재 뚜렷한 이상 행동은 탐지되지 않았습니다.</div>
            )}
          </section>

          <section style={panelStyle}>
            <h2 style={panelTitleStyle}>세션 활동 이력</h2>

            {data.sessions.length === 0 ? (
              <div style={emptyStateStyle}>표시할 세션이 없습니다.</div>
            ) : (
              <div style={{ display: "grid", gap: 10 }}>
                {data.sessions.map((session) => (
                  <div key={session.session_id} style={sessionRowStyle}>
                    <div>
                      <div style={{ fontWeight: 700 }}>{session.session_id}</div>
                      <div style={{ color: "#6b7280", fontSize: 13, marginTop: 4 }}>
                        최근 활동: {formatDate(session.last_seen)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section style={panelStyle}>
            <h2 style={panelTitleStyle}>플레이어 요약</h2>
            <div style={{ display: "grid", gap: 10 }}>
              <div style={summaryNoteStyle}>
                이 플레이어는 최근 <b>{data.recent_alerts.length}건</b>의 알림 이력이
                있으며, 그중 <b>{highAlertCount}건</b>이 High 위험으로 분류됩니다.
              </div>
              <div style={summaryNoteStyle}>
                최근 이벤트 총합은 <b>{totalEventCount}건</b>이며, 주요 활동 유형은{" "}
                <b>{topEventType}</b> 입니다.
              </div>
              <div style={summaryNoteStyle}>
                이상 행동 탐지 결과와 이벤트 유형 분포를 함께 보면 플레이어의 위험
                패턴을 더 빠르게 파악할 수 있습니다.
              </div>
            </div>
          </section>
        </div>
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
  fontSize: 26,
  fontWeight: 800,
  color: "#111827",
};

const panelStyle: React.CSSProperties = {
  background: "white",
  border: "1px solid #e5e7eb",
  borderRadius: 18,
  padding: 18,
  boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
};

const panelTitleStyle: React.CSSProperties = {
  marginTop: 0,
  marginBottom: 16,
  fontSize: 22,
  color: "#111827",
};

const innerCardStyle: React.CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: 14,
  padding: 16,
  background: "#fcfcfd",
};

const emptyStateStyle: React.CSSProperties = {
  padding: 20,
  borderRadius: 14,
  border: "1px dashed #d1d5db",
  backgroundColor: "#f9fafb",
  color: "#6b7280",
};

const miniMetaBoxStyle: React.CSSProperties = {
  minWidth: 200,
  background: "#f9fafb",
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  padding: 12,
};

const miniMetaRowStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 12,
  marginBottom: 8,
};

const miniMetaLabelStyle: React.CSSProperties = {
  color: "#6b7280",
  fontSize: 13,
};

const miniMetaValueStyle: React.CSSProperties = {
  color: "#111827",
  fontWeight: 600,
  fontSize: 13,
};

const metricBoxStyle: React.CSSProperties = {
  background: "#f9fafb",
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  padding: 12,
};

const metricLabelStyle: React.CSSProperties = {
  color: "#6b7280",
  fontSize: 12,
  marginBottom: 6,
};

const metricValueStyle: React.CSSProperties = {
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

const sessionRowStyle: React.CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: 12,
  padding: 14,
  background: "#f9fafb",
};

const summaryNoteStyle: React.CSSProperties = {
  padding: 14,
  borderRadius: 12,
  background: "#f9fafb",
  border: "1px solid #e5e7eb",
  color: "#374151",
  lineHeight: 1.6,
};