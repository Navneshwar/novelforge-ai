import React, { useState, useEffect } from 'react';
import api from '../services/api';

function ContextDisplay({ novelId, query, limit = 5 }) {
  const [context, setContext] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (novelId && query) {
      fetchContext();
    }
  }, [novelId, query]);

  const fetchContext = async () => {
    if (!query || query.length < 3) return;
    
    setLoading(true);
    try {
      const response = await api.post(`/memory/recall/${novelId}`, {
        query: query,
        limit: limit
      });
      setContext(response.data.items || []);
      setError(null);
    } catch (err) {
      setError('Failed to fetch context');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card" style={{ padding: '0.5rem 1rem' }}>
        <p style={{ fontSize: '0.85rem', color: '#a0a0b8' }}>🔍 Loading context...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" style={{ padding: '0.5rem 1rem', borderColor: '#ff4444' }}>
        <p style={{ fontSize: '0.85rem', color: '#ff6666' }}>{error}</p>
      </div>
    );
  }

  if (context.length === 0) {
    return null;
  }

  return (
    <div className="card" style={{ padding: '0.5rem 1rem', background: '#1a1a2a' }}>
      <h4 style={{ fontSize: '0.9rem', marginBottom: '0.3rem' }}>🧠 Related Memory</h4>
      {context.map((item, idx) => (
        <div 
          key={idx} 
          style={{ 
            padding: '0.3rem 0', 
            borderBottom: idx < context.length - 1 ? '1px solid #2a2a3a' : 'none',
            fontSize: '0.85rem'
          }}
        >
          <span style={{ color: '#6c63ff', fontWeight: 'bold' }}>[{item.type || 'memory'}]</span>
          {' '}
          <span>{item.text?.slice(0, 150) || item.content?.slice(0, 150) || '...'}</span>
          {item.relevance && (
            <span style={{ 
              float: 'right', 
              fontSize: '0.7rem', 
              color: '#10b981',
              background: '#1a2a1a',
              padding: '0.1rem 0.4rem',
              borderRadius: '8px'
            }}>
              {Math.round(item.relevance * 100)}% match
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

export default ContextDisplay;
