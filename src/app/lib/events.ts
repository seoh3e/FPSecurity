import type { SecurityEvent } from "../types/events";

export async function getEvents(): Promise<SecurityEvent[]> {
  const res = await fetch("http://localhost:3000/api/events", {
    cache: "no-store", // 항상 최신 데이터
  });

  if (!res.ok) {
    throw new Error("Failed to fetch events");
  }

  return res.json();
}