import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import NovelEditor from '../components/NovelEditor';
import GraphVisualizer from '../components/GraphVisualizer';
import ConsistencyPanel from '../components/ConsistencyPanel';
import CharacterList from '../components/CharacterList';

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
      const stats = await api.get(`/memory/stats/${id}`);
      setMemoryStats(stats.data);
    } catch (err) {
      setError('Failed to load novel');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const saveNovel = async (data) => {
    try {
      if (id === 'new') {
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

  return (
    <div>
      <div className="flex justify-between align-center mb-4">
        <div>
          <h1>{novel.title}</h1>
          <p style={{ color: '#a0a0b8' }}>{novel.genre} • {novel.chapters?.length || 0} chapters</p>
        </div>
        <div className="flex gap-2">
          <button 
            className={`btn ${activeTab === 'editor' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('editor')}
          >
            ✏️ Editor
          </button>
          <button 
            className={`btn ${activeTab === 'characters' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('characters')}
          >
            👥 Characters
          </button>
          <button 
            className={`btn ${activeTab === 'graph' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('graph')}
          >
            🕸️ Memory Graph
          </button>
          <button 
            className={`btn ${activeTab === 'consistency' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('consistency')}
          >
            ✓ Consistency
          </button>
        </div>
      </div>

      {memoryStats && (
        <div className="flex gap-4 mb-4" style={{ flexWrap: 'wrap' }}>
          <div className="card" style={{ padding: '0.8rem 1.2rem' }}>
            <small>Memory Items</small>
            <strong>{memoryStats.total_items || 0}</strong>
          </div>
          <div className="card" style={{ padding: '0.8rem 1.2rem' }}>
            <small>Characters</small>
            <strong>{memoryStats.characters || 0}</strong>
          </div>
          <div className="card" style={{ padding: '0.8rem 1.2rem' }}>
            <small>Plot Points</small>
            <strong>{memoryStats.plot_points || 0}</strong>
          </div>
          <div className="card" style={{ padding: '0.8rem 1.2rem' }}>
            <small>Relationships</small>
            <strong>{memoryStats.relationships || 0}</strong>
          </div>
        </div>
      )}

      <div style={{ marginTop: '1.5rem' }}>
        {activeTab === 'editor' && (
          <NovelEditor novel={novel} onSave={saveNovel} />
        )}
        {activeTab === 'characters' && (
          <CharacterList novelId={novel.id} characters={novel.characters || []} />
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