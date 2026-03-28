type Alert = {
  id: number;
  player_id: string;
  session_id: string;
  created_at: string;
  [key: string]: unknown;
};

type AlertsResponse = {
  total: number;
  limit: number;
  offset: number;
  items: Alert[];
};

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
    throw new Error("Failed to fetch alerts");
  }

  const data: AlertsResponse = await res.json();

  return (
    <main style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <h1>알림 목록</h1>
      <p>total: {data.total}</p>

      <div style={{ marginTop: 16 }}>
        {data.items.map((alert) => (
          <div
            key={alert.id}
            style={{
              border: "1px solid #e5e7eb",
              borderRadius: 12,
              padding: 16,
              marginBottom: 12,
              background: "white",
              color: "#111827",
            }}
          >
            <div>
              <strong>ID:</strong> {alert.id}
            </div>
            <div>
              <strong>Player:</strong> {alert.player_id}
            </div>
            <div>
              <strong>Session:</strong> {alert.session_id}
            </div>
            <div>
              <strong>Created At:</strong> {alert.created_at}
            </div>

            <pre style={{ whiteSpace: "pre-wrap", marginTop: 12 }}>
              {JSON.stringify(alert, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </main>
  );
}