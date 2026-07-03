import React, { useState, useEffect } from 'react';
import api from '../services/api';

function ConsistencyPanel({ novelId }) {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (novelId) {
      fetchIssues();
    }
  }, [novelId]);

  const fetchIssues = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/consistency/issues/${novelId}`);
      setIssues(response.data || []);
      setError(null);
    } catch (err) {
      setError('Failed to load consistency issues');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runConsistencyCheck = async () => {
    setChecking(true);
    try {
      const response = await api.post(`/consistency/check/${novelId}`);
      setIssues(response.data.issues || []);
      alert(`✅ Check complete! Found ${response.data.issues?.length || 0} issues.`);
    } catch (err) {
      alert('Failed to run consistency check');
      console.error(err);
    } finally {
      setChecking(false);
    }
  };

  const resolveIssue = async (issueId) => {
    try {
      await api.post(`/consistency/resolve/${novelId}/${issueId}`);
      setIssues(issues.filter(issue => issue.id !== issueId));
    } catch (err) {
      alert('Failed to resolve issue');
      console.error(err);
    }
  };

  const getIssueIcon = (type) => {
    const icons = {
      contradiction: '⚠️',
      character: '👤',
      plot: '📖',
      timeline: '⏰',
      location: '📍',
      consistency: '🔄',
    };
    return icons[type] || '❓';
  };

  const getIssueColor = (severity) => {
    const colors = {
      critical: '#ff4444',
      high: '#ff8844',
      medium: '#ffcc44',
      low: '#66bb6a',
    };
    return colors[severity] || '#ffcc44';
  };

  if (loading) {
    return (
      <div className="card" style={{ minHeight: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>🔍 Checking for inconsistencies...</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex justify-between align-center mb-4">
        <h3>✓ Consistency Checker</h3>
        <button 
          className="btn btn-primary" 
          onClick={runConsistencyCheck}
          disabled={checking}
        >
          {checking ? '🔍 Scanning...' : '🔍 Run Full Check'}
        </button>
      </div>

      {error && (
        <div className="card" style={{ background: '#2a1a1a', borderColor: '#ff4444' }}>
          <p style={{ color: '#ff6666' }}>{error}</p>
        </div>
      )}

      {issues.length === 0 ? (
        <div className="text-center" style={{ padding: '2rem' }}>
          <p style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</p>
          <h3>No Consistency Issues Found</h3>
          <p style={{ color: '#a0a0b8' }}>Your story is consistent! All characters, plots, and facts align.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <p style={{ color: '#a0a0b8', marginBottom: '1rem' }}>
            Found {issues.length} issue{issues.length > 1 ? 's' : ''} that need attention.
          </p>
          {issues.map((issue, index) => (
            <div 
              key={index}
              className="card" 
              style={{ 
                padding: '1rem',
                borderLeft: `4px solid ${getIssueColor(issue.severity)}`,
                background: '#1a1a2a'
              }}
            >
              <div className="flex justify-between align-start">
                <div>
                  <div className="flex gap-2 align-center">
                    <span style={{ fontSize: '1.2rem' }}>{getIssueIcon(issue.type)}</span>
                    <h4 style={{ margin: 0 }}>{issue.title || issue.type}</h4>
                    <span 
                      style={{ 
                        fontSize: '0.7rem', 
                        padding: '0.1rem 0.5rem', 
                        borderRadius: '12px',
                        background: getIssueColor(issue.severity),
                        color: '#0a0a0f',
                        fontWeight: 'bold'
                      }}
                    >
                      {issue.severity || 'medium'}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.95rem', marginTop: '0.5rem' }}>
                    {issue.description || issue.text}
                  </p>
                  {issue.location && (
                    <p style={{ fontSize: '0.8rem', color: '#6c63ff', marginTop: '0.3rem' }}>
                      📍 {issue.location}
                    </p>
                  )}
                  {issue.suggestion && (
                    <p style={{ fontSize: '0.85rem', color: '#10b981', marginTop: '0.3rem' }}>
                      💡 Suggestion: {issue.suggestion}
                    </p>
                  )}
                </div>
                {issue.id && (
                  <button 
                    className="btn btn-secondary" 
                    onClick={() => resolveIssue(issue.id)}
                    style={{ fontSize: '0.8rem' }}
                  >
                    ✓ Mark Resolved
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ConsistencyPanel;