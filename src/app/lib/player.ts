const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

export type PlayerResponse = {
  player_id: string;
  [key: string]: unknown;
};

export async function getPlayer(playerId: string): Promise<PlayerResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/players/${playerId}`, {
    headers: {
      "X-API-Key": API_KEY ?? "",
    },
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`플레이어 가져오기 실패: ${res.status}`);
  }

  return res.json();
}