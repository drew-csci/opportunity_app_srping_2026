import { useState, useEffect, useRef } from 'react';
import ConversationList from './ConversationList';
import ChatWindow from './ChatWindow';
import MessageInput from './MessageInput';
import FAQSuggestions from './FAQSuggestions';

export default function Messaging() {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [faqSuggestions, setFaqSuggestions] = useState([]);
  const messageListEndRef = useRef(null);

  // Fetch conversations on component mount
  useEffect(() => {
    fetchConversations();
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messageListEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Fetch messages when conversation changes
  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.id);
    }
  }, [selectedConversation]);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/conversations/', {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to fetch conversations');
      const data = await response.json();
      setConversations(data);
      if (data.length > 0 && !selectedConversation) {
        setSelectedConversation(data[0]);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      const response = await fetch(`/api/messages/?conversation_id=${conversationId}`, {
        credentials: 'include',
      });
      if (!response.ok) throw new Error('Failed to fetch messages');
      const data = await response.json();
      setMessages(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSendMessage = async (content) => {
    if (!selectedConversation) return;

    try {
      const response = await fetch('/api/messages/send/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'include',
        body: JSON.stringify({
          conversation_id: selectedConversation.id,
          content: content,
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');
      const newMessage = await response.json();
      setMessages([...messages, newMessage]);

      // Fetch FAQ suggestions after sending
      fetchFaqSuggestions(content);

      // Update conversation last message
      fetchConversations();
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchFaqSuggestions = async (messageContent) => {
    try {
      const response = await fetch('/api/faq-suggestions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'include',
        body: JSON.stringify({
          message_content: messageContent,
        }),
      });

      if (!response.ok) throw new Error('Failed to fetch FAQ suggestions');
      const data = await response.json();
      setFaqSuggestions(data);
    } catch (err) {
      console.error('Error fetching FAQ suggestions:', err);
    }
  };

  const handleConversationSelect = (conversation) => {
    setSelectedConversation(conversation);
    setFaqSuggestions([]);
  };

  const handleCreateConversation = async (organizationId) => {
    try {
      const response = await fetch('/api/conversations/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        credentials: 'include',
        body: JSON.stringify({
          organization_id: organizationId,
        }),
      });

      if (!response.ok) throw new Error('Failed to create conversation');
      const newConversation = await response.json();
      setConversations([newConversation, ...conversations]);
      setSelectedConversation(newConversation);
    } catch (err) {
      setError(err.message);
    }
  };

  const getCsrfToken = () => {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  if (loading) {
    return <div className="messaging-loading">Loading conversations...</div>;
  }

  if (error) {
    return <div className="messaging-error">Error: {error}</div>;
  }

  return (
    <div className="messaging-container" style={{ display: 'flex', height: '100vh' }}>
      <div className="messaging-sidebar" style={{ width: '25%', borderRight: '1px solid #ddd', overflowY: 'auto' }}>
        <ConversationList
          conversations={conversations}
          selectedConversation={selectedConversation}
          onConversationSelect={handleConversationSelect}
          onCreateConversation={handleCreateConversation}
        />
      </div>

      <div className="messaging-main" style={{ width: '75%', display: 'flex', flexDirection: 'column' }}>
        {selectedConversation ? (
          <>
            <ChatWindow
              conversation={selectedConversation}
              messages={messages}
              messageListEndRef={messageListEndRef}
            />
            <FAQSuggestions suggestions={faqSuggestions} />
            <MessageInput onSendMessage={handleSendMessage} />
          </>
        ) : (
          <div className="messaging-empty" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <p>Select a conversation to start messaging</p>
          </div>
        )}
      </div>
    </div>
  );
}


