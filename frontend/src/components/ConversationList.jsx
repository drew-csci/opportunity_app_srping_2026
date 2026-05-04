import { useState } from 'react';

export default function ConversationList({
  conversations,
  selectedConversation,
  onConversationSelect,
  onCreateConversation,
}) {
  const [organizations, setOrganizations] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loadingOrgs, setLoadingOrgs] = useState(false);

  const handleShowCreateForm = async () => {
    if (!showCreateForm && organizations.length === 0) {
      setLoadingOrgs(true);
      try {
        const response = await fetch('/api/organizations/', {
          credentials: 'include',
        });
        if (response.ok) {
          const data = await response.json();
          setOrganizations(data);
        }
      } catch (err) {
        console.error('Error loading organizations:', err);
      } finally {
        setLoadingOrgs(false);
      }
    }
    setShowCreateForm(!showCreateForm);
  };

  const handleSelectOrganization = (orgId) => {
    onCreateConversation(orgId);
    setShowCreateForm(false);
  };

  return (

    <div
      style={{
        width: 280,
        border: "1px solid #ddd",
        borderRadius: 10,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          padding: 10,
          borderBottom: "1px solid #eee",
          fontWeight: 700,
        }}
      >
        Conversations
        <button
          onClick={handleShowCreateForm}
          style={{
            float: 'right',
            padding: '5px 10px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
          }}
        >
          + New
        </button>
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

            {conversation.volunteer_name && (
              <div style={{ fontSize: 12, color: "#666" }}>
                {conversation.volunteer_name}
              </div>
            )}

            {conversation.last_message_at && (
              <div style={{ fontSize: 12, color: "#666", marginTop: 4 }}>
                {new Date(conversation.last_message_at).toLocaleString()}
              </div>
            )}
          </button>
        ))
      )}

      <div style={{ flex: 1, overflowY: 'auto' }}>
        {conversations.length === 0 ? (
          <div style={{ padding: 12, color: '#666' }}>No conversations yet</div>
        ) : (
          conversations.map((conversation) => (
            <button
              key={conversation.id}
              type="button"
              onClick={() => onConversationSelect(conversation)}
              style={{
                width: '100%',
                textAlign: 'left',
                padding: 10,
                border: 'none',
                borderBottom: '1px solid #f1f1f1',
                background: selectedConversation?.id === conversation.id ? '#f5f8ff' : 'white',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
              }}
            >
              <div style={{ fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {conversation.other_user?.display_name || 'Unknown'}
              </div>
              <div style={{ fontSize: 12, color: '#666', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {conversation.last_message || 'No messages yet'}
              </div>
              <div style={{ fontSize: 10, color: '#999' }}>
                {new Date(conversation.last_message_at).toLocaleDateString()}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}