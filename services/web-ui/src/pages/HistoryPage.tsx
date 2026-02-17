import { useEffect, useState } from "react";
import { listSubmissions } from "../api/client";
import type { Submission } from "../types";

interface HistoryPageProps {
  token: string;
}

export function HistoryPage({ token }: HistoryPageProps) {
  const [items, setItems] = useState<Submission[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    let isCancelled = false;
    setLoading(true);
    setError(null);
    listSubmissions(token, page, pageSize)
      .then((response) => {
        if (isCancelled) {
          return;
        }
        setItems(response.items);
        setTotal(response.total);
      })
      .catch((err) => {
        if (!isCancelled) {
          setError(err instanceof Error ? err.message : "Failed to load history");
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [token, page, pageSize]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const canPrev = page > 1 && !loading;
  const canNext = page < totalPages && !loading;

  return (
    <div className="app-shell">
      <div className="card">
        <h1 className="title">Submission History</h1>
        <div className="kv">
          <strong>Page</strong>
          <span>
            {page} / {totalPages}
          </span>
        </div>
        <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
          <button className="btn secondary" type="button" disabled={!canPrev} onClick={() => setPage((p) => p - 1)}>
            Previous
          </button>
          <button className="btn secondary" type="button" disabled={!canNext} onClick={() => setPage((p) => p + 1)}>
            Next
          </button>
        </div>
        {error ? <p className="error">{error}</p> : null}
        {loading ? <p className="small">Loading submissions...</p> : null}
        {!loading && items.length === 0 ? <p className="small">No submissions yet.</p> : null}
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
