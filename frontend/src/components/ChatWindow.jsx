export default function ChatWindow({
  organization,
  messages,
  input,
  setInput,
  onSend,
  suggestions,
}) {
  function bubbleStyle(sender) {
    const isMe = sender === "volunteer";
    return {
      maxWidth: "70%",
      padding: 10,
      borderRadius: 12,
      marginBottom: 8,
      alignSelf: isMe ? "flex-end" : "flex-start",
      background: isMe ? "#e8f0ff" : "#f2f2f2",
    };
  }

  return (
    <div style={{ flex: 1, border: "1px solid #ddd", borderRadius: 10, padding: 12 }}>
      <div style={{ fontWeight: "bold", marginBottom: 10 }}>Chat with: {organization}</div>

      <div
        style={{
          border: "1px solid #eee",
          borderRadius: 10,
          padding: 12,
          height: 320,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          background: "white",
        }}
      >
        {messages.map((m) => (
          <div key={m.id} style={bubbleStyle(m.sender_type)}>
            <div style={{ fontSize: 12, color: "#555" }}>{m.sender_type}</div>
            <div>{m.content}</div>
            <div style={{ fontSize: 11, color: "#999" }}>
              {new Date(m.created_at).toLocaleString()}
            </div>
          </div>
        ))}
      </div>

      {/* ✅ AI-assisted FAQ suggestions (MVP) */}
      <div style={{ marginTop: 12 }}>
        <div style={{ fontWeight: "bold", marginBottom: 6 }}>AI-assisted FAQ suggestions</div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => setInput(s)}
              style={{
                border: "1px solid #ddd",
                borderRadius: 999,
                padding: "8px 12px",
                cursor: "pointer",
                background: "white",
              }}
            >
              {s}
            </button>
          ))}
          {suggestions.length === 0 && (
            <span style={{ color: "#777", fontSize: 13 }}>No suggestions</span>
          )}
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          style={{ flex: 1, padding: 10, borderRadius: 10, border: "1px solid #ddd" }}
          onKeyDown={(e) => {
            if (e.key === "Enter") onSend();
          }}
        />
        <button onClick={onSend}>Send</button>
      </div>
    </div>
  );
}