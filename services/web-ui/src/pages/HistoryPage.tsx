import { useEffect, useState } from "react";
import { listSubmissions } from "../api/client";
import type { Submission } from "../types";

interface HistoryPageProps {
  token: string;
}

export function HistoryPage({ token }: HistoryPageProps) {
  const [items, setItems] = useState<Submission[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listSubmissions(token)
      .then((response) => setItems(response.items))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load history"));
  }, [token]);

  return (
    <div className="app-shell">
      <div className="card">
        <h1 className="title">Submission History</h1>
        {error ? <p className="error">{error}</p> : null}
        {items.length === 0 ? <p className="small">No submissions yet.</p> : null}
        {items.map((item) => (
          <div className="history-item" key={item.id}>
            <div className="kv">
              <strong>ID</strong>
              <span className="mono">{item.id}</span>
            </div>
            <div className="kv">
              <strong>Status</strong>
              <span>{item.status}</span>
            </div>
            <div className="kv">
              <strong>Language</strong>
              <span>{item.language ?? "unknown"}</span>
            </div>
            <div className="kv">
              <strong>Created</strong>
              <span>{new Date(item.created_at).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
