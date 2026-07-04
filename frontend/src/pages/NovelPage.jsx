import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import NovelEditor from '../components/NovelEditor';
import CharacterPanel from '../components/CharacterPanel';
import ConsistencyChecker from '../components/ConsistencyChecker';
import MemoryGraph from '../components/MemoryGraph';

function NovelPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [novel, setNovel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('editor');

  useEffect(() => {
    if (id && id !== 'new') {
      fetchNovel();
    } else {
      setLoading(false);
    }
  }, [id]);

  const fetchNovel = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/novels/${id}`);
      setNovel(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load novel');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 'var(--spacing-xl)' }}>
        <p>Loading novel...</p>
      </div>
    );
  }

  if (error && id !== 'new') {
    return (
      <div className="card" style={{ borderColor: 'var(--secondary-coral)', background: 'rgba(255, 107, 91, 0.05)' }}>
        <p style={{ color: 'var(--secondary-coral)' }}>⚠️ {error}</p>
        <button className="btn btn-primary" onClick={() => navigate('/')}>Back to Dashboard</button>
      </div>
    );
  }

  return (
    <div className="novel-page">
      {/* Tab Navigation */}
      <div className="novel-tabs">
        <button
          className={`tab-button ${activeTab === 'editor' ? 'active' : ''}`}
          onClick={() => setActiveTab('editor')}
        >
          ✍️ Editor
        </button>
        <button
          className={`tab-button ${activeTab === 'characters' ? 'active' : ''}`}
          onClick={() => setActiveTab('characters')}
        >
          👥 Characters
        </button>
        <button
          className={`tab-button ${activeTab === 'consistency' ? 'active' : ''}`}
          onClick={() => setActiveTab('consistency')}
        >
          🔍 Consistency
        </button>
        <button
          className={`tab-button ${activeTab === 'memory' ? 'active' : ''}`}
          onClick={() => setActiveTab('memory')}
        >
          🧠 Memory Graph
        </button>
      </div>

      {/* Content */}
      <div className="novel-content">
        {activeTab === 'editor' && (
          <NovelEditor novelId={id === 'new' ? null : id} novel={novel} onUpdate={() => fetchNovel()} />
        )}
        {activeTab === 'characters' && (
          <CharacterPanel novelId={id === 'new' ? null : id} novel={novel} />
        )}
        {activeTab === 'consistency' && (
          <ConsistencyChecker novelId={id === 'new' ? null : id} novel={novel} />
        )}
        {activeTab === 'memory' && (
          <MemoryGraph novelId={id === 'new' ? null : id} novel={novel} />
        )}
      </div>
    </div>
  );
}

export default NovelPage;
