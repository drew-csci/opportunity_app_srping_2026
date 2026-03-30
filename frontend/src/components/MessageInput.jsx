import { useState } from 'react';

export default function MessageInput({ onSendMessage }) {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    const text = input.trim();
    if (!text) return;

    setIsLoading(true);
    try {
      await onSendMessage(text);
      setInput('');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', gap: 8, padding: 15, borderTop: '1px solid #eee', backgroundColor: '#f9f9f9' }}>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your message... (Shift+Enter for new line)"
        style={{
          flex: 1,
          padding: 10,
          borderRadius: 8,
          border: '1px solid #ccc',
          fontFamily: 'inherit',
          resize: 'none',
          height: '60px',
        }}
        disabled={isLoading}
      />
      <button
        onClick={handleSend}
        disabled={isLoading || !input.trim()}
        style={{
          padding: '10px 20px',
          backgroundColor: input.trim() ? '#007bff' : '#ccc',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          cursor: input.trim() ? 'pointer' : 'not-allowed',
          fontWeight: 600,
          transition: 'background-color 0.2s',
        }}
      >
        {isLoading ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
}
