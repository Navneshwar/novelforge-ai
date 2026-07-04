import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import CreateNovelModal from '../components/CreateNovelModal';

function Dashboard() {
  const [novels, setNovels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const navigate = useNavigate();

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

  const handleCreateNovel = async (novelData) => {
    try {
      const response = await api.post('/novels', novelData);
      setShowCreateModal(false);
      navigate(`/novel/${response.data.id}`);
    } catch (err) {
      alert('Failed to create novel');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div style={{ textAlign: 'center', padding: 'var(--spacing-xl)' }}>
          <p>Loading your novels...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Hero Section */}
      <section className="hero-section">
        <h1>Welcome to NovelForge</h1>
        <p>Your AI-powered writing companion with persistent memory. Create novels with perfect consistency across characters, plots, and world-building.</p>
        <div className="hero-actions">
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            ✨ Start Writing
          </button>
          <button className="btn btn-secondary">
            📚 Browse Examples
          </button>
        </div>
      </section>

      {/* Novels Section */}
      <section className="novels-section">
        <div className="section-header">
          <h2>Your Novels</h2>
          <p>Continue your stories or start something new</p>
        </div>

        {error && (
          <div className="card" style={{ borderColor: 'var(--secondary-coral)', background: 'rgba(255, 107, 91, 0.05)' }}>
            <p style={{ color: 'var(--secondary-coral)' }}>⚠️ {error}</p>
          </div>
        )}

        {novels.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📖</div>
            <h3>No novels yet</h3>
            <p>Start your creative journey by creating your first novel. NovelForge will remember every character, plot point, and detail.</p>
            <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
              Create Your First Novel
            </button>
          </div>
        ) : (
          <div className="novels-grid">
            {novels.map((novel) => (
              <Link
                key={novel.id}
                to={`/novel/${novel.id}`}
                className="novel-card"
                style={{ textDecoration: 'none', color: 'inherit' }}
              >
                <div className="novel-card-header">
                  <h3 className="novel-card-title">{novel.title}</h3>
                </div>

                {novel.description && (
                  <p style={{ marginBottom: 'var(--spacing-md)', fontSize: '0.95rem' }}>
                    {novel.description.substring(0, 120)}...
                  </p>
                )}

                <div className="novel-card-meta">
                  {novel.genre && (
                    <div className="novel-card-stat">
                      <small>Genre</small>
                      <span className="genre-badge">{novel.genre}</span>
                    </div>
                  )}
                  <div className="novel-card-stat">
                    <small>Chapters</small>
                    <strong>{novel.chapters_count || 0}</strong>
                  </div>
                  <div className="novel-card-stat">
                    <small>Words</small>
                    <strong>{(novel.word_count || 0).toLocaleString()}</strong>
                  </div>
                </div>

                {novel.characters && novel.characters.length > 0 && (
                  <div style={{ marginTop: 'var(--spacing-md)', display: 'flex', gap: 'var(--spacing-xs)', flexWrap: 'wrap' }}>
                    {novel.characters.slice(0, 3).map((char) => (
                      <span key={char} className="badge badge-primary">
                        {char}
                      </span>
                    ))}
                    {novel.characters.length > 3 && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--primary-coral)' }}>
                        +{novel.characters.length - 3} more
                      </span>
                    )}
                  </div>
                )}

                {novel.last_edited && (
                  <small style={{ color: 'var(--text-light)', marginTop: 'var(--spacing-md)', display: 'block' }}>
                    Last edited: {new Date(novel.last_edited).toLocaleDateString()}
                  </small>
                )}
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Create Novel Modal */}
      <CreateNovelModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreate={handleCreateNovel}
      />
    </div>
  );
}

export default Dashboard;