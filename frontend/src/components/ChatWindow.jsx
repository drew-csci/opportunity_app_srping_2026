import { useState } from "react";

export default function ChatWindow({
  organization,
  messages,
  onSendMessage,
  suggestions = [],
}) {
  const [input, setInput] = useState("");

  function handleSend() {
    const text = input.trim();
    if (!text) return;
    onSendMessage(text);
    setInput("");
  }

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
    <div
      style={{
        flex: 1,
        border: "1px solid #ddd",
        borderRadius: 10,
        overflow: "hidden",
        padding: 12,
      }}
    >
      <div
        style={{
          fontWeight: "bold",
          marginBottom: 10,
          borderBottom: "1px solid #eee",
          paddingBottom: 10,
        }}
      >
        Chat with: {organization}
      </div>

      <div
        aria-label="chat-messages"
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
        {messages.map((message) => (
          <div key={message.id} style={bubbleStyle(message.sender_type)}>
            <div style={{ fontSize: 12, color: "#555" }}>
              {message.sender_type}
            </div>
            <div>{message.content}</div>
            {message.created_at && (
              <div style={{ fontSize: 11, color: "#999" }}>
                {new Date(message.created_at).toLocaleString()}
              </div>
            )}
          </div>
        ))}
      </div>

      <div style={{ marginTop: 12 }}>
        <div style={{ fontWeight: "bold", marginBottom: 6 }}>
          AI-assisted FAQ suggestions
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              type="button"
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

      <div
        style={{
          display: "flex",
          gap: 8,
          marginTop: 12,
          paddingTop: 10,
          borderTop: "1px solid #eee",
        }}
      >
        <input
          aria-label="message-input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Type a message..."
          style={{
            flex: 1,
            padding: 10,
            borderRadius: 10,
            border: "1px solid #ddd",
          }}
          onKeyDown={(event) => {
            if (event.key === "Enter") handleSend();
          }}
        />
        <button type="button" onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
}