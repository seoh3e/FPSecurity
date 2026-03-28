import { getEvents } from "../lib/events";

export default async function EventsPage() {
  const data = await getEvents();

  return (
    <main style={{ padding: "24px" }}>
      <h1>이벤트 목록</h1>
      <p>total: {data.total}</p>

      <pre style={{ whiteSpace: "pre-wrap", marginTop: "16px" }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </main>
  );
}