export default function FAQSuggestions({ suggestions }) {
  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div style={{ 
      padding: 15, 
      borderTop: '1px solid #e0e0e0', 
      backgroundColor: '#f0f9ff',
      maxHeight: '150px',
      overflowY: 'auto'
    }}>
      <div style={{ fontWeight: 600, marginBottom: 10, fontSize: '14px', color: '#333' }}>
        💡 AI-Assisted FAQ Suggestions:
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {suggestions.map((suggestion, index) => (
          <div
            key={index}
            style={{
              padding: 10,
              backgroundColor: 'white',
              borderRadius: 6,
              border: '1px solid #d0d0d0',
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              ':hover': {
                backgroundColor: '#e8f4fd',
              }
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#e8f4fd';
              e.currentTarget.style.borderColor = '#007bff';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
              e.currentTarget.style.borderColor = '#d0d0d0';
            }}
          >
            <div style={{ fontWeight: 500, color: '#007bff', marginBottom: '4px' }}>
              Suggestion {index + 1} (Relevance: {(suggestion.relevance_score * 100).toFixed(0)}%)
            </div>
            <div style={{ color: '#555' }}>
              {suggestion.faq_content}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
