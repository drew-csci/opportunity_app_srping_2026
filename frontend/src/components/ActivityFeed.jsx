import { useEffect, useMemo, useState } from "react";

const DEFAULT_API_BASE = "http://localhost:8000";

const mockFeed = [
  {
    id: 1,
    volunteer_name: "Tin Tin Do",
    organization_name: "Red Cross",
    title: "Tutored students",
    created_at: "2026-02-27T18:00:00Z",
  },
  {
    id: 2,
    volunteer_name: "Ryan",
    organization_name: "Food Bank",
    title: "Distributed food packages",
    created_at: "2026-02-26T15:30:00Z",
  },
  {
    id: 3,
    volunteer_name: "Nakiwe",
    organization_name: "Community Center",
    title: "Organized a community event",
    created_at: "2026-02-25T20:10:00Z",
  },
];

export function normalizeActivityItems(raw) {
  const items = Array.isArray(raw) ? raw : raw?.items ?? raw?.data ?? [];
  return (items || []).map((x, idx) => ({
    id: x.id ?? `${idx}`,
    volunteer_name: x.volunteer_name ?? x.volunteerName ?? "Unknown",
    organization_name: x.organization_name ?? x.organizationName ?? "Unknown",
    title: x.title ?? "Untitled",
    created_at: x.created_at ?? x.createdAt ?? new Date().toISOString(),
  }));
}

async function defaultFetchActivityFeed({ apiBase, limit }) {
  const res = await fetch(`${apiBase}/api/feed?limit=${limit}`);
  if (!res.ok) throw new Error("backend unavailable");
  return await res.json();
}

export default function ActivityFeed({
  apiBase = import.meta?.env?.VITE_API_BASE ?? DEFAULT_API_BASE,
  limit = 20,
  fetchActivityFeed = defaultFetchActivityFeed,
  fallbackItems = mockFeed,
}) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usingMock, setUsingMock] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setLoading(true);
        setUsingMock(false);

        const data = await fetchActivityFeed({ apiBase, limit });
        if (cancelled) return;
        setItems(normalizeActivityItems(data));
      } catch {
        if (cancelled) return;
        setUsingMock(true);
        setItems(normalizeActivityItems(fallbackItems));
      } finally {
        if (cancelled) return;
        setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [apiBase, fallbackItems, fetchActivityFeed, limit]);

  const isEmpty = useMemo(() => !loading && items.length === 0, [loading, items.length]);

  return (
    <div>
      <h2>Peer Activity Feed</h2>

      <div style={{ fontSize: 12, color: "#666", marginBottom: 10 }}>
        Data source: {usingMock ? "Mock (backend not ready)" : "API /api/feed"}
      </div>

      {loading && <p>Loading...</p>}

      {isEmpty && <p>No recent activity available</p>}

      {!loading && items.length > 0 && (
        <div
          aria-label="activity-feed"
          style={{
            border: "1px solid #ddd",
            borderRadius: 10,
            padding: 12,
            height: 360,
            overflowY: "auto",
            background: "white",
            textAlign: "left",
          }}
        >
          {items.map((it) => (
            <div
              key={it.id}
              style={{
                padding: 12,
                borderBottom: "1px solid #eee",
              }}
            >
              <div style={{ fontWeight: 700 }}>{it.volunteer_name}</div>
              <div style={{ margin: "4px 0" }}>{it.title}</div>
              <div style={{ color: "#666" }}>{it.organization_name}</div>
              <div style={{ fontSize: 12, color: "#999", marginTop: 6 }}>
                {new Date(it.created_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

