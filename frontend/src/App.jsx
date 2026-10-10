import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";

const empty = { topic: "", notes: "", hours: "1" };

export default function App() {
  const [entries, setEntries] = useState([]);
  const [stats, setStats] = useState(null);
  const [healthy, setHealthy] = useState(null); // null = checking
  const [form, setForm] = useState(empty);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      const [list, s] = await Promise.all([api.list(), api.stats()]);
      setEntries(list);
      setStats(s);
      setError("");
    } catch {
      setError("Could not reach the API.");
    }
  }, []);

  const checkHealth = useCallback(async () => {
    try {
      await api.health();
      setHealthy(true);
    } catch {
      setHealthy(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    checkHealth();
    const timer = setInterval(checkHealth, 15000);
    return () => clearInterval(timer);
  }, [refresh, checkHealth]);

  async function submit(e) {
    e.preventDefault();
    try {
      await api.add({
        topic: form.topic.trim(),
        notes: form.notes.trim(),
        hours: Number(form.hours),
      });
      setForm(empty);
      refresh();
    } catch {
      setError("Could not save. Check the topic and hours (0 to 24).");
    }
  }

  async function remove(id) {
    await api.remove(id);
    refresh();
  }

  return (
    <main>
      <header>
        <div>
          <h1>Learning Tracker</h1>
          <p className="sub">React → Nginx → FastAPI → PostgreSQL</p>
        </div>
        <div className="status">
          <span className={"dot " + (healthy === null ? "" : healthy ? "up" : "down")} />
          {healthy === null ? "checking…" : healthy ? "API and database up" : "API unreachable"}
        </div>
      </header>

      {stats && (
        <section className="stats">
          <div><strong>{stats.entries}</strong><span>entries</span></div>
          <div><strong>{stats.total_hours}</strong><span>hours</span></div>
          <div><strong>{stats.top_topic ?? "-"}</strong><span>top topic</span></div>
        </section>
      )}

      <form onSubmit={submit}>
        <input
          placeholder="What did you learn? (e.g. Docker networking)"
          value={form.topic}
          maxLength={200}
          required
          onChange={(e) => setForm({ ...form, topic: e.target.value })}
        />
        <textarea
          placeholder="Notes (optional)"
          rows={2}
          value={form.notes}
          onChange={(e) => setForm({ ...form, notes: e.target.value })}
        />
        <div className="row">
          <label>
            Hours
            <input
              type="number"
              min="0.25"
              max="24"
              step="0.25"
              value={form.hours}
              required
              onChange={(e) => setForm({ ...form, hours: e.target.value })}
            />
          </label>
          <button type="submit">Add entry</button>
        </div>
      </form>

      {error && <p className="error">{error}</p>}

      <ul>
        {entries.length === 0 && <li className="empty">No entries yet. Add what you learned today.</li>}
        {entries.map((e) => (
          <li key={e.id}>
            <div className="grow">
              <h2>{e.topic}</h2>
              {e.notes && <p>{e.notes}</p>}
              <small>
                {e.hours} h · {new Date(e.created_at).toLocaleDateString()}
              </small>
            </div>
            <button className="ghost" onClick={() => remove(e.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </main>
  );
}
