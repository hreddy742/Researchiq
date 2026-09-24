const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function startResearch(query: string): Promise<string> {
  const res = await fetch(`${BASE_URL}/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail ?? "Failed to start research");
  }
  const data = await res.json();
  return data.session_id as string;
}

export function openResearchStream(sessionId: string): EventSource {
  return new EventSource(`${BASE_URL}/research/${sessionId}/stream`);
}
