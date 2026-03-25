export default function ConversationList({ conversations, activeId, onSelect }) {
  return (
    <div style={{ width: 280, border: "1px solid #ddd", borderRadius: 10, padding: 12 }}>
      <div style={{ fontWeight: "bold", marginBottom: 10 }}>Organizations</div>

      {conversations.length === 0 && <div>No conversations</div>}

      {conversations.map((c) => (
        <button
          key={c.id}
          onClick={() => onSelect(c.id)}
          style={{
            width: "100%",
            textAlign: "left",
            padding: 10,
            marginBottom: 8,
            borderRadius: 10,
            border: c.id === activeId ? "2px solid #333" : "1px solid #ddd",
            background: "white",
            cursor: "pointer",
          }}
        >
          <div style={{ fontWeight: "bold" }}>{c.organization_name}</div>
          <div style={{ fontSize: 12, color: "#666" }}>
            {new Date(c.last_message_at).toLocaleString()}
          </div>
        </button>
      ))}
    </div>
  );
}