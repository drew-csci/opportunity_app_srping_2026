import { useEffect, useMemo, useState } from "react";
import ConversationList from "./ConversationList";
import ChatWindow from "./ChatWindow";

const API_BASE = "http://localhost:8000";

// Fallback mocks (khi backend chưa xong)
const mockConversations = [
  {
    id: 1,
    volunteer_name: "Tin Tin Do",
    organization_name: "Red Cross",
    last_message_at: "2026-02-27T18:00:00Z",
  },
  {
    id: 2,
    volunteer_name: "Tin Tin Do",
    organization_name: "Food Bank",
    last_message_at: "2026-02-26T16:00:00Z",
  },
];

const mockMessagesByConvId = {
  1: [
    {
      id: 11,
      conversation_id: 1,
      sender_type: "volunteer",
      content: "Hi, I have a question about this opportunity.",
      created_at: "2026-02-27T18:00:00Z",
    },
    {
      id: 12,
      conversation_id: 1,
      sender_type: "organization",
      content: "Sure! What would you like to know?",
      created_at: "2026-02-27T18:01:00Z",
    },
  ],
  2: [
    {
      id: 21,
      conversation_id: 2,
      sender_type: "volunteer",
      content: "Hello, is this role remote or in-person?",
      created_at: "2026-02-26T16:00:00Z",
    },
    {
      id: 22,
      conversation_id: 2,
      sender_type: "organization",
      content: "Mostly in-person, some remote coordination.",
      created_at: "2026-02-26T16:02:00Z",
    },
  ],
};

// ✅ FAQ suggestions MVP (luôn hiện)
const FAQ_SUGGESTIONS = [
  "Where is the location?",
  "What skills are required?",
  "What is the schedule?",
];

function normalizeConvs(convs) {
  return (convs || []).map((c, idx) => ({
    id: c.id ?? idx,
    volunteer_name: c.volunteer_name ?? "Tin Tin Do",
    organization_name: c.organization_name ?? "Unknown Org",
    last_message_at: c.last_message_at ?? new Date().toISOString(),
  }));
}

function normalizeMsgs(msgs, conversation_id) {
  return (msgs || []).map((m, idx) => ({
    id: m.id ?? `m-${conversation_id}-${idx}`,
    conversation_id: m.conversation_id ?? conversation_id,
    sender_type: m.sender_type ?? "volunteer",
    content: m.content ?? "",
    created_at: m.created_at ?? new Date().toISOString(),
  }));
}

export default function Messaging() {
  const volunteerName = "Tin Tin Do";

  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const [usingMock, setUsingMock] = useState(false);

  const activeConversation = useMemo(
    () => conversations.find((c) => c.id === activeId),
    [conversations, activeId]
  );

  useEffect(() => {
    loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (activeId) loadMessages(activeId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeId]);

  async function loadConversations() {
    try {
      setUsingMock(false);
      const res = await fetch(
        `${API_BASE}/api/conversations?volunteer_name=${encodeURIComponent(volunteerName)}`
      );
      if (!res.ok) throw new Error("API not ready");
      const data = normalizeConvs(await res.json());
      setConversations(data);
      setActiveId((prev) => prev ?? (data[0]?.id ?? null));
    } catch {
      setUsingMock(true);
      const data = normalizeConvs(mockConversations);
      setConversations(data);
      setActiveId((prev) => prev ?? (data[0]?.id ?? null));
    }
  }

  async function loadMessages(conversationId) {
    try {
      if (usingMock) {
        setMessages(normalizeMsgs(mockMessagesByConvId[conversationId] || [], conversationId));
        return;
      }
      const res = await fetch(`${API_BASE}/api/conversations/${conversationId}/messages`);
      if (!res.ok) throw new Error("API not ready");
      const data = normalizeMsgs(await res.json(), conversationId);
      setMessages(data);
    } catch {
      setMessages(normalizeMsgs(mockMessagesByConvId[conversationId] || [], conversationId));
    }
  }

  async function onSend() {
    if (!activeId) return;
    const text = input.trim();
    if (!text) return;

    // optimistic UI
    const optimistic = {
      id: "tmp-" + Math.random(),
      conversation_id: activeId,
      sender_type: "volunteer",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimistic]);
    setInput("");

    // if mock mode → just keep optimistic
    if (usingMock) return;

    try {
      const res = await fetch(`${API_BASE}/api/conversations/${activeId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sender_type: "volunteer", content: text }),
      });
      if (!res.ok) throw new Error("send failed");

      // reload canonical messages
      await loadMessages(activeId);
      await loadConversations();
    } catch {
      // if API fails mid-send, switch to mock mode but keep UI working
      setUsingMock(true);
    }
  }

  return (
    <div>
      <h2>US-011 — Messaging (Volunteer)</h2>
      <div style={{ fontSize: 12, color: "#666", marginBottom: 10 }}>
        Data source: {usingMock ? "Mock (backend not ready)" : "API (conversations/messages)"}
      </div>

      <div style={{ display: "flex", gap: 12 }}>
        <ConversationList
          conversations={conversations}
          activeId={activeId}
          onSelect={setActiveId}
        />

        {activeConversation ? (
          <ChatWindow
            organization={activeConversation.organization_name}
            messages={messages}
            input={input}
            setInput={setInput}
            onSend={onSend}
            suggestions={FAQ_SUGGESTIONS} // ✅ always visible chips
          />
        ) : (
          <div style={{ flex: 1, border: "1px solid #ddd", borderRadius: 10, padding: 12 }}>
            Select an organization to start messaging.
          </div>
        )}
      </div>
    </div>
  );
}