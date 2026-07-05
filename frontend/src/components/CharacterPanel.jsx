import React, { useState, useEffect } from 'react';
import api from '../services/api';

function CharacterPanel({ novelId, novel }) {
  const [characters, setCharacters] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', role: '', description: '', traits: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (novel?.characters) {
      setCharacters(Array.isArray(novel.characters) ? novel.characters : []);
    }
  }, [novel]);

  const handleAddCharacter = async (e) => {
    e.preventDefault();
    if (!novelId || !formData.name.trim()) return;

    setLoading(true);
    try {
      const response = await api.post(`/characters/${novelId}`, {
        name: formData.name,
        role: formData.role,
        description: formData.description,
        traits: formData.traits.split(',').map(t => t.trim()).filter(t => t)
      });
      setCharacters([...characters, response.data]);
      setFormData({ name: '', role: '', description: '', traits: '' });
      setShowForm(false);
    } catch (err) {
      alert('Failed to add character');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="character-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-lg)' }}>
        <div>
          <h2>Characters</h2>
          <p>Manage your novel's characters and relationships</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)} disabled={!novelId}>
          + Add Character
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
          <form onSubmit={handleAddCharacter}>
            <div className="modal-field">
              <label>Character Name *</label>
              <input
                type="text"
                placeholder="e.g., Alara Moonwhisper"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div className="modal-field">
              <label>Role</label>
              <select value={formData.role} onChange={(e) => setFormData({ ...formData, role: e.target.value })}>
                <option value="">Select role...</option>
                <option value="protagonist">Protagonist</option>
                <option value="antagonist">Antagonist</option>
                <option value="supporting">Supporting</option>
                <option value="minor">Minor</option>
              </select>
            </div>

            <div className="modal-field">
              <label>Description</label>
              <textarea
                placeholder="Physical appearance, background, motivations..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                style={{ minHeight: '80px' }}
              />
            </div>

            <div className="modal-field">
              <label>Traits (comma-separated)</label>
              <input
                type="text"
                placeholder="e.g., brave, intelligent, mysterious"
                value={formData.traits}
                onChange={(e) => setFormData({ ...formData, traits: e.target.value })}
              />
            </div>

            <div className="modal-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Adding...' : 'Add Character'}
              </button>
            </div>
          </form>
        </div>
      )}

      {characters.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">👥</div>
          <h3>No characters yet</h3>
          <p>Add characters to your novel to track them in the memory system</p>
        </div>
      ) : (
        <div className="grid">
          {characters.map((char) => (
            <div key={char.id} className="card">
              <h3>{char.name}</h3>
              {char.role && <span className="badge badge-primary">{char.role}</span>}
              {char.description && <p style={{ margin: 'var(--spacing-sm) 0' }}>{char.description}</p>}
              {char.traits && char.traits.length > 0 && (
                <div style={{ display: 'flex', gap: 'var(--spacing-xs)', flexWrap: 'wrap', marginTop: 'var(--spacing-sm)' }}>
                  {char.traits.map((trait) => (
                    <span key={trait} className="badge badge-secondary">{trait}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CharacterPanel;
