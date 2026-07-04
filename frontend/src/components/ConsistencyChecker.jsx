import React, { useState } from 'react';
import api from '../services/api';

function ConsistencyChecker({ novelId, novel }) {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasRun, setHasRun] = useState(false);

  const handleRunCheck = async () => {
    if (!novelId) return;
    setLoading(true);
    try {
      const response = await api.post(`/novels/${novelId}/consistency/check`);
      setIssues(response.data.issues || []);
      setHasRun(true);
    } catch (err) {
      alert('Failed to run consistency check');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="consistency-panel">
      <div style={{ marginBottom: 'var(--spacing-lg)' }}>
        <h2>Consistency Checker</h2>
        <p>Automatically detect contradictions and inconsistencies in your narrative</p>
      </div>

      <button className="btn btn-primary" onClick={handleRunCheck} disabled={!novelId || loading}>
        {loading ? '⏳ Running Check...' : '🔍 Run Full Check'}
      </button>

      {hasRun && (
        <div style={{ marginTop: 'var(--spacing-lg)' }}>
          {issues.length === 0 ? (
            <div className="card" style={{ background: 'rgba(16, 185, 129, 0.05)', borderColor: '#10b981' }}>
              <p style={{ color: '#10b981' }}>✓ No consistency issues found!</p>
            </div>
          ) : (
            <div>
              <h3 style={{ marginBottom: 'var(--spacing-md)' }}>Found {issues.length} Issue{issues.length !== 1 ? 's' : ''}</h3>
              <div className="grid">
                {issues.map((issue, idx) => (
                  <div key={idx} className="card" style={{ borderLeft: '4px solid var(--secondary-coral)' }}>
                    <div style={{ display: 'flex', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-sm)' }}>
                      <span className="badge badge-secondary">{issue.type}</span>
                      {issue.severity && <span className="badge badge-neutral">{issue.severity}</span>}
                    </div>
                    <h4>{issue.title}</h4>
                    <p>{issue.description}</p>
                    {issue.suggestion && (
                      <p style={{ marginTop: 'var(--spacing-sm)', padding: 'var(--spacing-sm)', background: 'var(--bg-cream)', borderRadius: 'var(--radius-md)' }}>
                        <strong>Suggestion:</strong> {issue.suggestion}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ConsistencyChecker;
