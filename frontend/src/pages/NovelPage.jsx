import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import NovelEditor from '../components/NovelEditor';
import GraphVisualizer from '../components/GraphVisualizer';
import ConsistencyPanel from '../components/ConsistencyPanel';
import CharacterList from '../components/CharacterList';
import WorldBuilding from '../components/WorldBuilding';
import Timeline from '../components/Timeline';

function NovelPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [novel, setNovel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('editor');
  const [memoryStats, setMemoryStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (id && id !== 'new') {
      fetchNovel();
    } else {
      setLoading(false);
      setNovel({ title: 'Untitled Novel', genre: 'General', chapters: [] });
    }
  }, [id]);

  const fetchNovel = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/novels/${id}`);
      setNovel(response.data);
      setError(null);
      
      // Fetch memory stats
      try {
        const stats = await api.get(`/memory/stats/${id}`);
        setMemoryStats(stats.data);
      } catch (statsErr) {
        console.warn('Memory stats unavailable:', statsErr);
      }
    } catch (err) {
      setError('Failed to load novel');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const saveNovel = async (data) => {
    try {
      if (id === 'new' || !id) {
        const response = await api.post('/novels', data);
        navigate(`/novel/${response.data.id}`);
      } else {
        await api.put(`/novels/${id}`, data);
        await fetchNovel();
      }
    } catch (err) {
      alert('Failed to save novel');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="text-center" style={{ padding: '4rem' }}>
        <p>Loading novel...</p>
      </div>
    );
  }

  if (error || !novel) {
    return (
      <div className="text-center" style={{ padding: '4rem' }}>
        <h3>Novel not found</h3>
        <button className="btn btn-primary mt-4" onClick={() => navigate('/')}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  const tabs = [
    { key: 'editor', icon: '✏️', label: 'Editor' },
    { key: 'characters', icon: '👥', label: 'Characters' },
    { key: 'world', icon: '🌍', label: 'World' },
    { key: 'timeline', icon: '📅', label: 'Timeline' },
    { key: 'graph', icon: '🕸️', label: 'Memory Graph' },
    { key: 'consistency', icon: '✓', label: 'Consistency' },
  ];

  return (
    <div>
      <div className="flex justify-between align-center mb-4" style={{ flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1>{novel.title}</h1>
          <div className="flex gap-2 align-center" style={{ flexWrap: 'wrap' }}>
            {novel.genre && novel.genre.split(',').map((g, i) => (
              <span key={i} className="genre-badge">{g.trim()}</span>
            ))}
            <span style={{ color: '#a0a0b8', fontSize: '0.9rem' }}>
              • {novel.chapters?.length || 0} chapters
            </span>
          </div>
        </div>
        <div className="tab-bar">
          {tabs.map(tab => (
            <button
              key={tab.key}
              className={`tab-btn ${activeTab === tab.key ? 'tab-btn-active' : ''}`}
              onClick={() => setActiveTab(tab.key)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {memoryStats && (
        <div className="stats-bar mb-4">
          <div className="stat-chip">
            <small>Memory Items</small>
            <strong>{memoryStats.total_items || 0}</strong>
          </div>
          <div className="stat-chip">
            <small>Characters</small>
            <strong>{memoryStats.characters || 0}</strong>
          </div>
          <div className="stat-chip">
            <small>Plot Points</small>
            <strong>{memoryStats.plot_points || 0}</strong>
          </div>
          <div className="stat-chip">
            <small>Relationships</small>
            <strong>{memoryStats.relationships || 0}</strong>
          </div>
        </div>
      )}

      <div style={{ marginTop: '1rem' }}>
        {activeTab === 'editor' && (
          <NovelEditor novel={novel} onSave={saveNovel} />
        )}
        {activeTab === 'characters' && (
          <CharacterList novelId={novel.id} characters={novel.characters || []} />
        )}
        {activeTab === 'world' && (
          <WorldBuilding novelId={novel.id} />
        )}
        {activeTab === 'timeline' && (
          <Timeline novelId={novel.id} />
        )}
        {activeTab === 'graph' && (
          <GraphVisualizer novelId={novel.id} />
        )}
        {activeTab === 'consistency' && (
          <ConsistencyPanel novelId={novel.id} />
        )}
      </div>
    </div>
  );
}

export default NovelPage;