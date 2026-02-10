import { getEvents } from "../lib/events";
import EventsClient from "./EventsClient";

export default async function EventsPage() {
  const events = await getEvents();

  return (
    <main style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <header style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
        <h1 style={{ margin: 0 }}>Security Events</h1>
        <span style={{ opacity: 0.7 }}>관리자 탐지 이벤트 목록</span>
      </header>

      {/* ✅ Client-side filtering / sorting UI */}
      <EventsClient events={events} />

      <div style={{ height: 10 }} />
      <p style={{ opacity: 0.65, margin: 0 }}>
        * 현재는 목데이터(MOCK)이며, 이후 백엔드 API로 교체 예정
      </p>
    </main>
  );
}
