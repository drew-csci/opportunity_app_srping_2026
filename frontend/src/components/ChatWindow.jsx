export default function ChatWindow({ conversation, messages, messageListEndRef }) {
  const getOtherUserName = () => {
    if (!conversation) return 'Unknown';
    return conversation.other_user?.display_name || 'Unknown';
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', borderRight: '1px solid #ddd' }}>
      <div style={{ padding: 15, borderBottom: '1px solid #eee', fontWeight: 700, backgroundColor: '#f9f9f9' }}>
        {getOtherUserName()}
      </div>

      <div
        aria-label="chat-messages"
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 15,
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
          background: '#fff',
        }}
      >
        {messages && messages.length > 0 ? (
          messages.map((message) => (
            <div
              key={message.id}
              style={{
                alignSelf: message.sender.id === conversation?.volunteer?.id ? 'flex-end' : 'flex-start',
                maxWidth: '70%',
              }}
            >
              <div
                style={{
                  background: message.sender.id === conversation?.volunteer?.id ? '#007bff' : '#e9ecef',
                  color: message.sender.id === conversation?.volunteer?.id ? 'white' : 'black',
                  borderRadius: 10,
                  padding: '10px 12px',
                  wordWrap: 'break-word',
                }}
              >
                {message.content}
              </div>
              <small style={{ display: 'block', marginTop: '4px', color: '#999', textAlign: message.sender.id === conversation?.volunteer?.id ? 'right' : 'left' }}>
                {formatTime(message.timestamp)}
              </small>
            </div>
          ))
        ) : (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#999' }}>
            No messages yet. Start the conversation!
          </div>
        )}
        <div ref={messageListEndRef} />
      </div>
    </div>
  );
}

