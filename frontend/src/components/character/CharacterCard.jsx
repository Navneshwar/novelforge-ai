import React from 'react';
import { Users, Heart, Zap } from 'lucide-react';
import '../styles/CharacterCard.css';

const CharacterCard = ({ character, isCompact = false }) => {
  if (isCompact) {
    return (
      <div className="character-card-compact">
        <div className="character-avatar" style={{ backgroundColor: character.color }}>
          {character.name[0]}
        </div>
        <div className="character-info-compact">
          <h4>{character.name}</h4>
          <p>{character.role}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="character-card">
      {/* Portrait Section */}
      <div className="character-portrait">
        <div
          className="portrait-placeholder"
          style={{ backgroundColor: character.color }}
        >
          <div className="portrait-text">
            {character.name[0]}{character.name.split(' ')[1]?.[0]}
          </div>
        </div>
      </div>

      <div className="character-divider" />

      {/* Character Info */}
      <div className="character-details">
        <div className="detail-row">
          <span className="detail-label">Character</span>
          <span className="detail-value">{character.name}</span>
        </div>

        <div className="detail-row">
          <span className="detail-label">Role</span>
          <span className="detail-value">{character.role}</span>
        </div>

        <div className="detail-row">
          <span className="detail-label">Age</span>
          <span className="detail-value">{character.age || 'Unknown'}</span>
        </div>

        {/* Traits Section */}
        <div className="traits-section">
          <span className="detail-label">Traits</span>
          <div className="traits-list">
            {character.traits?.map((trait, index) => (
              <span key={index} className="trait-badge">
                {trait}
              </span>
            ))}
          </div>
        </div>

        {/* Relationships & Development */}
        <div className="character-stats">
          <div className="stat">
            <Users size={16} />
            <span>{character.relationshipCount || 0} Relationships</span>
          </div>
          <div className="stat">
            <Heart size={16} />
            <span>{character.mentions || 0} Mentions</span>
          </div>
          <div className="stat">
            <Zap size={16} />
            <span>{character.development || 0}% Growth</span>
          </div>
        </div>
      </div>

      <div className="character-divider" />
    </div>
  );
};

export default CharacterCard;
