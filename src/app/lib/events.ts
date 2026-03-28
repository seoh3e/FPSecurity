const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

export type EventItem = {
  id: number;
  player_id: string;
  session_id: string;
  created_at: string;
  event_count: number;
  payload: unknown;
};

export type EventsResponse = {
  total: number;
  limit: number;
  offset: number;
  items: EventItem[];
};

export async function getEvents(): Promise<EventsResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/events?limit=50&offset=0`, {
    headers: {
      "X-API-Key": API_KEY ?? "",
    },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`이벤트 가져오기 실패: ${res.status}`);
  }

  return res.json();
}