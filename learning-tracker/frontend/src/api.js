// All calls to the backend live here. Paths start with /api (Nginx forwards them).
async function request(path, options) {
  const res = await fetch("/api" + path, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.status === 204 ? null : res.json();
}

export const api = {
  health: () => request("/health"),
  stats: () => request("/stats"),
  list: () => request("/entries"),
  add: (entry) =>
    request("/entries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entry),
    }),
  remove: (id) => request(`/entries/${id}`, { method: "DELETE" }),
};
