import React, { useState, useEffect } from 'react';
import api from '../services/api';

function CharacterList({ novelId, characters }) {
  const [charactersList, setCharactersList] = useState(characters || []);
  const [newCharacterName, setNewCharacterName] = useState('');
  const [newCharacterDescription, setNewCharacterDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCharacter, setSelectedCharacter] = useState(null);

  useEffect(() => {
    if (novelId) {
      fetchCharacters();
    }
  }, [novelId]);

  const fetchCharacters = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/characters/${novelId}`);
      setCharactersList(response.data || []);
    } catch (err) {
      console.error('Failed to fetch characters:', err);
    } finally {
      setLoading(false);
    }
  };

  const addCharacter = async () => {
    if (!newCharacterName.trim()) {
      alert('Please enter a character name.');
      return;
    }

    try {
      const response = await api.post(`/characters/${novelId}`, {
        name: newCharacterName,
        description: newCharacterDescription,
      });
      setCharactersList([...charactersList, response.data]);
      setNewCharacterName('');
      setNewCharacterDescription('');
    } catch (err) {
      alert('Failed to add character');
      console.error(err);
    }
  };

  const deleteCharacter = async (charId) => {
    if (!window.confirm('Delete this character?')) return;
    
    try {
      await api.delete(`/characters/${novelId}/${charId}`);
      setCharactersList(charactersList.filter(c => c.id !== charId));
    } catch (err) {
      alert('Failed to delete character');
      console.error(err);
    }
  };

  const generateCharacterBackstory = async (charId) => {
    try {
      const response = await api.post(`/characters/${novelId}/${charId}/generate-backstory`);
      
      alert(`📖 Backstory generated for ${response.data.character_name}:\n\n${response.data.backstory.slice(0, 300)}...`);
      
      // Refresh characters to show updated backstory
      await fetchCharacters();
    } catch (err) {
      alert('Failed to generate backstory');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <p>Loading characters...</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>👥 Characters</h3>
      
      <div className="flex gap-4 mb-4" style={{ flexWrap: 'wrap' }}>
        <div style={{ flex: 2 }}>
          <label>Character Name</label>
          <input
            type="text"
            value={newCharacterName}
            onChange={(e) => setNewCharacterName(e.target.value)}
            placeholder="Enter character name"
          />
        </div>
        <div style={{ flex: 3 }}>
          <label>Description</label>
          <input
            type="text"
            value={newCharacterDescription}
            onChange={(e) => setNewCharacterDescription(e.target.value)}
            placeholder="Brief description or role"
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
          <button className="btn btn-primary" onClick={addCharacter}>
            + Add Character
          </button>
        </div>
      </div>

      {charactersList.length === 0 ? (
        <div className="text-center" style={{ padding: '2rem' }}>
          <p style={{ fontSize: '3rem' }}>📝</p>
          <p>No characters yet. Add your first character!</p>
        </div>
      ) : (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))' }}>
          {charactersList.map((char) => (
            <div 
              key={char.id} 
              className="card" 
              style={{ 
                padding: '1rem',
                background: selectedCharacter?.id === char.id ? '#1a1a2a' : '#14141e',
                cursor: 'pointer'
              }}
              onClick={() => setSelectedCharacter(char)}
            >
              <div className="flex justify-between align-start">
                <div>
                  <h4 style={{ margin: 0, color: '#6c63ff' }}>{char.name}</h4>
                  {char.description && (
                    <p style={{ fontSize: '0.85rem', marginTop: '0.3rem', color: '#a0a0b8' }}>
                      {char.description}
                    </p>
                  )}
                  {char.traits && (
                    <div style={{ display: 'flex', gap: '0.3rem', flexWrap: 'wrap', marginTop: '0.3rem' }}>
                      {char.traits.map((trait, idx) => (
                        <span key={idx} style={{ 
                          background: '#2a2a3a', 
                          padding: '0.1rem 0.5rem', 
                          borderRadius: '12px',
                          fontSize: '0.7rem'
                        }}>
                          {trait}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <button 
                    className="btn btn-secondary" 
                    onClick={(e) => { e.stopPropagation(); generateCharacterBackstory(char.id); }}
                    style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem' }}
                  >
                    📖
                  </button>
                  <button 
                    className="btn btn-secondary" 
                    onClick={(e) => { e.stopPropagation(); deleteCharacter(char.id); }}
                    style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', color: '#ff4444' }}
                  >
                    ✕
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedCharacter && (
        <div className="card mt-4" style={{ background: '#1a1a2a', borderColor: '#6c63ff' }}>
          <h4>Character Details: {selectedCharacter.name}</h4>
          <p><strong>Role:</strong> {selectedCharacter.role || 'Not specified'}</p>
          <p><strong>Description:</strong> {selectedCharacter.description || 'No description'}</p>
          {selectedCharacter.relationships && (
            <div>
              <strong>Relationships:</strong>
              <div className="flex gap-2" style={{ flexWrap: 'wrap', marginTop: '0.3rem' }}>
                {selectedCharacter.relationships.map((rel, idx) => (
                  <span key={idx} style={{ 
                    background: '#2a2a3a', 
                    padding: '0.2rem 0.6rem', 
                    borderRadius: '12px',
                    fontSize: '0.8rem'
                  }}>
                    {rel}
                  </span>
                ))}
              </div>
            </div>
          )}
          <button 
            className="btn btn-secondary mt-4" 
            onClick={() => setSelectedCharacter(null)}
            style={{ fontSize: '0.8rem' }}
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}

export default CharacterList;