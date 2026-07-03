import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

function Dashboard() {
  const [novels, setNovels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchNovels();
  }, []);

  const fetchNovels = async () => {
    try {
      setLoading(true);
      const response = await api.get('/novels');
      setNovels(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load novels');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createNewNovel = async () => {
    try {
      const response = await api.post('/novels', {
        title: 'Untitled Novel',
        genre: 'General',
      });
      window.location.href = `/novel/${response.data.id}`;
    } catch (err) {
      alert('Failed to create novel');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="text-center" style={{ padding: '4rem' }}>
        <p>Loading your novels...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between align-center mb-4">
        <h1>📚 Your Novels</h1>
        <button className="btn btn-primary" onClick={createNewNovel}>
          + New Novel
        </button>
      </div>

      {error && (
        <div className="card" style={{ background: '#2a1a1a', borderColor: '#ff4444', marginBottom: '1rem' }}>
          <p style={{ color: '#ff6666' }}>{error}</p>
        </div>
      )}

      {novels.length === 0 ? (
        <div className="card text-center" style={{ padding: '4rem' }}>
          <h3>No novels yet</h3>
          <p style={{ margin: '1rem 0' }}>Start your first novel with AI-powered memory!</p>
          <button className="btn btn-primary" onClick={createNewNovel}>
            Create Your First Novel
          </button>
        </div>
      ) : (
        <div className="grid">
          {novels.map((novel) => (
            <Link to={`/novel/${novel.id}`} key={novel.id} style={{ textDecoration: 'none' }}>
              <div className="card">
                <h3>{novel.title}</h3>
                <p style={{ fontSize: '0.9rem' }}>
                  {novel.genre} • {novel.chapters?.length || 0} chapters
                </p>
                <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
                  Last updated: {new Date(novel.updated_at).toLocaleDateString()}
                </p>
                {novel.characters && (
                  <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    {novel.characters.slice(0, 3).map((char) => (
                      <span key={char} style={{ 
                        background: '#2a2a3a', 
                        padding: '0.2rem 0.6rem', 
                        borderRadius: '12px',
                        fontSize: '0.75rem'
                      }}>
                        {char}
                      </span>
                    ))}
                    {novel.characters.length > 3 && (
                      <span style={{ fontSize: '0.75rem', color: '#6c63ff' }}>
                        +{novel.characters.length - 3} more
                      </span>
                    )}
                  </div>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;