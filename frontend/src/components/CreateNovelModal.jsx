import React from 'react';

function CreateNovelModal({ isOpen, onClose, onCreate }) {
  const [title, setTitle] = React.useState('');
  const [genre, setGenre] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const genres = [
    'Fantasy', 'Science Fiction', 'Romance', 'Mystery', 'Thriller',
    'Horror', 'Adventure', 'Drama', 'Historical Fiction', 'Poetry'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert('Please enter a novel title');
      return;
    }

    setLoading(true);
    try {
      await onCreate({
        title: title.trim(),
        genre: genre || 'General',
        description: description.trim()
      });
      setTitle('');
      setGenre('');
      setDescription('');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Novel</h2>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          <div className="modal-field">
            <label htmlFor="title">Novel Title</label>
            <input
              id="title"
              type="text"
              placeholder="Enter your novel's title..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoFocus
            />
          </div>

          <div className="modal-field">
            <label htmlFor="genre">Genre</label>
            <select
              id="genre"
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
            >
              <option value="">Select a genre...</option>
              {genres.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>

          <div className="modal-field">
            <label htmlFor="description">Description (Optional)</label>
            <textarea
              id="description"
              placeholder="Describe your novel's premise, setting, or plot..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{ minHeight: '100px' }}
            />
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Novel'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateNovelModal;