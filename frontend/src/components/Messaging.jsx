import { useMemo, useState } from "react";
import ConversationList from "./ConversationList";
import ChatWindow from "./ChatWindow";

const mockConversations = [
  {
    id: 1,
    volunteer_name: "Tin Tin Do",
    organization_name: "Red Cross",
  },
  {
    id: 2,
    volunteer_name: "Tin Tin Do",
    organization_name: "Food Bank",
  },
];

const mockMessagesByConversation = {
  1: [
    {
      id: 101,
      sender_type: "organization",
      content: "Hi! Thanks for reaching out. How can we help?",
    },
  ],
  2: [
    {
      id: 201,
      sender_type: "organization",
      content: "Welcome! Ask us anything about volunteering.",
    },
  ],
};

function getMockFaqResponse(text) {
  const lowered = text.toLowerCase();
  if (lowered.includes("hours")) {
    return "Our volunteer hours are Monday-Friday, 9:00 AM to 5:00 PM.";
  }
  return "Thanks for your message. We will get back to you soon.";
}

export default function Messaging() {
  const [conversations] = useState(mockConversations);
  const [activeId, setActiveId] = useState(mockConversations[0]?.id ?? null);
  const [messagesByConversation, setMessagesByConversation] = useState(mockMessagesByConversation);

  const activeConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === activeId) ?? null,
    [activeId, conversations]
  );

  const activeMessages = activeConversation ? messagesByConversation[activeConversation.id] ?? [] : [];

  function handleSendMessage(text) {
    if (!activeConversation) return;

    const userMessage = {
      id: Date.now(),
      sender_type: "volunteer",
      content: text,
    };

    setMessagesByConversation((previous) => ({
      ...previous,
      [activeConversation.id]: [...(previous[activeConversation.id] ?? []), userMessage],
    }));

    const faqResponse = {
      id: Date.now() + 1,
      sender_type: "organization",
      content: getMockFaqResponse(text),
    };

    setTimeout(() => {
      setMessagesByConversation((previous) => ({
        ...previous,
        [activeConversation.id]: [...(previous[activeConversation.id] ?? []), faqResponse],
      }));
    }, 300);
  }

  return (
    <div>
      <h2>US-011 Messaging</h2>
      <div style={{ display: "flex", gap: 12 }}>
        <ConversationList conversations={conversations} activeId={activeId} onSelect={setActiveId} />
        {activeConversation ? (
          <ChatWindow
            organization={activeConversation.organization_name}
            messages={activeMessages}
            onSendMessage={handleSendMessage}
          />
        ) : (
          <div style={{ flex: 1, border: "1px solid #ddd", borderRadius: 10, padding: 12 }}>
            Select a conversation to start messaging.
          </div>
        )}
      </div>
    </div>
  );
}

