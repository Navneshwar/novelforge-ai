import React, { useState } from 'react';

const GENRES = [
  'Fantasy', 'Sci-Fi', 'Mystery', 'Romance', 'Horror', 'Thriller',
  'Historical', 'Literary', 'Adventure', 'Dark Fantasy', 'Dystopian',
  'Urban Fantasy', 'Crime', 'Comedy', 'Drama', 'Supernatural',
  'Steampunk', 'Cyberpunk', 'Magical Realism', 'Young Adult'
];

function CreateNovelModal({ isOpen, onClose, onCreate }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [writingStyle, setWritingStyle] = useState('');
  const [targetWordCount, setTargetWordCount] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const toggleGenre = (genre) => {
    setSelectedGenres(prev =>
      prev.includes(genre)
        ? prev.filter(g => g !== genre)
        : [...prev, genre]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onCreate({
        title: title.trim(),
        genre: selectedGenres.length > 0 ? selectedGenres.join(', ') : 'General',
        description: description.trim(),
        writing_style: writingStyle.trim(),
        target_word_count: targetWordCount ? parseInt(targetWordCount) : null,
      });
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal-container">
        <div className="modal-header">
          <h2 style={{ margin: 0, fontSize: '1.6rem' }}>✨ Create New Novel</h2>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          {/* Title */}
          <div className="modal-field">
            <label className="modal-label">Novel Title <span style={{ color: '#ff6b6b' }}>*</span></label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter your novel's title..."
              className="modal-input"
              autoFocus
            />
          </div>

          {/* Genres - Multi select */}
          <div className="modal-field">
            <label className="modal-label">
              Genres
              {selectedGenres.length > 0 && (
                <span style={{ color: '#6c63ff', fontWeight: 400, marginLeft: '0.5rem' }}>
                  ({selectedGenres.length} selected)
                </span>
              )}
            </label>
            <div className="genre-grid">
              {GENRES.map(genre => (
                <button
                  key={genre}
                  type="button"
                  className={`genre-chip ${selectedGenres.includes(genre) ? 'genre-chip-selected' : ''}`}
                  onClick={() => toggleGenre(genre)}
                >
                  {genre}
                </button>
              ))}
            </div>
          </div>

          {/* Description */}
          <div className="modal-field">
            <label className="modal-label">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief synopsis or premise of your novel..."
              className="modal-input"
              rows={3}
              style={{ resize: 'vertical' }}
            />
          </div>

          {/* Row: Writing Style + Target Word Count */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <div className="modal-field" style={{ flex: 2 }}>
              <label className="modal-label">Writing Style</label>
              <input
                type="text"
                value={writingStyle}
                onChange={(e) => setWritingStyle(e.target.value)}
                placeholder="e.g., First person, lyrical prose..."
                className="modal-input"
              />
            </div>
            <div className="modal-field" style={{ flex: 1 }}>
              <label className="modal-label">Target Word Count</label>
              <input
                type="number"
                value={targetWordCount}
                onChange={(e) => setTargetWordCount(e.target.value)}
                placeholder="e.g., 80000"
                className="modal-input"
                min="0"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!title.trim() || isSubmitting}
              style={{ minWidth: '140px' }}
            >
              {isSubmitting ? '✨ Creating...' : '📖 Create Novel'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateNovelModal;
