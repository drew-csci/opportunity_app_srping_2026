import { useState } from "react";

export default function ChatWindow({ organization, messages, onSendMessage }) {
  const [input, setInput] = useState("");

  function handleSend() {
    const text = input.trim();
    if (!text) return;
    onSendMessage(text);
    setInput("");
  }

  return (
    <div style={{ flex: 1, border: "1px solid #ddd", borderRadius: 10, overflow: "hidden" }}>
      <div style={{ padding: 10, borderBottom: "1px solid #eee", fontWeight: 700 }}>{organization}</div>

      <div
        aria-label="chat-messages"
        style={{
          height: 280,
          overflowY: "auto",
          padding: 12,
          display: "flex",
          flexDirection: "column",
          gap: 8,
          background: "#fff",
        }}
      >
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              alignSelf: message.sender_type === "volunteer" ? "flex-end" : "flex-start",
              maxWidth: "80%",
              background: message.sender_type === "volunteer" ? "#dce9ff" : "#f3f3f3",
              borderRadius: 10,
              padding: "8px 10px",
            }}
          >
            <div>{message.content}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8, padding: 10, borderTop: "1px solid #eee" }}>
        <input
          aria-label="message-input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Type your message..."
          style={{ flex: 1, padding: 8, borderRadius: 8, border: "1px solid #ccc" }}
        />
        <button type="button" onClick={handleSend}>
          Send
        </button>
      </div>
    </div>
  );
}

