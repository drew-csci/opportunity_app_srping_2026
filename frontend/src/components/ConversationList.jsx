export default function ConversationList({ conversations, activeId, onSelect }) {
  return (
    <div style={{ width: 280, border: "1px solid #ddd", borderRadius: 10, overflow: "hidden" }}>
      <div style={{ padding: 10, borderBottom: "1px solid #eee", fontWeight: 700 }}>
        Conversations
      </div>
      {conversations.length === 0 ? (
        <div style={{ padding: 12, color: "#666" }}>No conversations</div>
      ) : (
        conversations.map((conversation) => (
          <button
            key={conversation.id}
            type="button"
            onClick={() => onSelect(conversation.id)}
            style={{
              width: "100%",
              textAlign: "left",
              padding: 10,
              border: "none",
              borderBottom: "1px solid #f1f1f1",
              background: activeId === conversation.id ? "#f5f8ff" : "white",
              cursor: "pointer",
            }}
          >
            <div style={{ fontWeight: 600 }}>{conversation.organization_name}</div>
            <div style={{ fontSize: 12, color: "#666" }}>{conversation.volunteer_name}</div>
          </button>
        ))
      )}
    </div>
  );
}

