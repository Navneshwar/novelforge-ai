import React from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Clock, Zap } from 'lucide-react';
import '../styles/NovelCard.css';

const NovelCard = ({ novel, isHighlight = false }) => {
  const progress = novel.progress || 68;
  const genreColors = {
    fantasy: '#B38A63',
    scifi: '#7B9BA4',
    horror: '#C16D6D',
    romance: '#D4A574',
    mystery: '#7D5D3E',
    default: '#B38A63',
  };

  const genreColor = genreColors[novel.genre?.toLowerCase()] || genreColors.default;

  return (
    <Link to={`/novel/${novel.id}`} className={`novel-card ${isHighlight ? 'highlight' : ''}`}>
      {/* Cover Image */}
      <div
        className="novel-card-cover"
        style={{
          background: `linear-gradient(135deg, ${genreColor}40 0%, ${genreColor}20 100%)`,
        }}
      >
        <div className="cover-icon">
          <BookOpen size={48} color={genreColor} strokeWidth={1} />
        </div>
        <div className="genre-badge" style={{ backgroundColor: genreColor }}>
          {novel.genre}
        </div>
      </div>

      {/* Content */}
      <div className="novel-card-content">
        <h3 className="novel-card-title">{novel.title}</h3>
        
        <p className="novel-card-meta">
          {novel.chapterCount} chapters · {novel.wordCount?.toLocaleString()} words
        </p>

        {/* Progress Bar */}
        <div className="progress-section">
          <div className="progress-header">
            <span className="progress-label">Progress</span>
            <span className="progress-value">{progress}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {/* Quick Stats */}
        <div className="novel-card-stats">
          <div className="stat">
            <Clock size={16} />
            <span>Updated {novel.updatedAt}</span>
          </div>
          <div className="stat">
            <Zap size={16} />
            <span>AI Ready</span>
          </div>
        </div>

        {/* Hover Overlay */}
        <div className="card-overlay">
          <span className="continue-text">Continue Writing →</span>
        </div>
      </div>
    </Link>
  );
};

export default NovelCard;
