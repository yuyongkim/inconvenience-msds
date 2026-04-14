const API_BASE = "/api";

export function apiUrl(path) {
  return `${API_BASE}${path.startsWith("/") ? "" : "/"}${path}`;
}

export async function apiGet(path, { signal } = {}) {
  const r = await fetch(apiUrl(path), { signal });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return await r.json();
}

export async function apiPostJson(path, body, { signal } = {}) {
  const r = await fetch(apiUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
    signal,
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return await r.json();
}

