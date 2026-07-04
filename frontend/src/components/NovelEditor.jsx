import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import api from '../services/api';

function NovelEditor({ novel, onSave }) {
  const [title, setTitle] = useState(novel?.title || '');
  const [genre, setGenre] = useState(novel?.genre || 'General');
  const [content, setContent] = useState(novel?.content || '');
  const [chapters, setChapters] = useState(novel?.chapters || []);
  const [currentChapter, setCurrentChapter] = useState(novel?.chapters?.length || 0);
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [memoryContext, setMemoryContext] = useState([]);
  const [showMemory, setShowMemory] = useState(false);

  useEffect(() => {
    if (novel?.id) {
      fetchMemoryContext();
    }
  }, [novel?.id, content]);

  const fetchMemoryContext = async () => {
    try {
      const response = await api.post(`/memory/recall/${novel.id}`, {
        query: content.slice(-500) || 'story context',
        limit: 5
      });
      setMemoryContext(response.data.items || []);
    } catch (err) {
      console.error('Failed to fetch memory context:', err);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave({
        title,
        genre,
        content,
        chapters
      });
      await fetchMemoryContext();
    } catch (err) {
      alert('Failed to save');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAIWrite = async () => {
    if (!content.trim()) {
      alert('Please write some content first to continue from.');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await api.post(`/memory/recall/${novel.id}`, {
        query: content.slice(-300),
        limit: 3
      });

      const context = (response.data.items || []).map(item => item.text).join('\n');
      
      const generateResponse = await api.post(`/novels/${novel.id}/generate`, {
        prompt: content,
        context: context,
        style: 'continue'
      });

      setContent(content + '\n\n' + generateResponse.data.generated_text);
    } catch (err) {
      alert('Failed to generate content');
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCharacterExtract = async () => {
    if (!content.trim()) {
      alert('Please write some content first.');
      return;
    }

    try {
      const response = await api.post(`/novels/${novel.id}/extract-characters`, {
        text: content
      });
      
      alert(`Extracted ${response.data.characters.length} characters: ${response.data.characters.join(', ')}`);
      await fetchMemoryContext();
    } catch (err) {
      alert('Failed to extract characters');
      console.error(err);
    }
  };

  return (
    <div className="card" style={{ padding: '2rem' }}>
      <div className="flex flex-col gap-4">
        <div className="flex gap-4" style={{ flexWrap: 'wrap' }}>
          <div style={{ flex: 2 }}>
            <label>Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Novel Title"
            />
          </div>
          <div style={{ flex: 1 }}>
            <label>Genre</label>
            <select value={genre} onChange={(e) => setGenre(e.target.value)}>
              <option>General</option>
              <option>Fantasy</option>
              <option>Sci-Fi</option>
              <option>Mystery</option>
              <option>Romance</option>
              <option>Horror</option>
              <option>Thriller</option>
            </select>
          </div>
        </div>

        <div>
          <div className="flex justify-between align-center">
            <label>Content</label>
            <div className="flex gap-2">
              <button 
                className="btn btn-secondary" 
                onClick={() => setShowMemory(!showMemory)}
                style={{ fontSize: '0.85rem' }}
              >
                {showMemory ? 'Hide Memory' : 'Show Memory Context'}
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={handleCharacterExtract}
                style={{ fontSize: '0.85rem' }}
              >
                Extract Characters
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handleAIWrite}
                disabled={isGenerating}
                style={{ fontSize: '0.85rem' }}
              >
                {isGenerating ? '✍️ Generating...' : '✍️ AI Continue'}
              </button>
            </div>
          </div>
          
          {showMemory && memoryContext.length > 0 && (
            <div className="card" style={{ margin: '0.5rem 0', background: '#1a1a2a' }}>
              <h4 style={{ fontSize: '0.9rem', marginBottom: '0.5rem' }}>🧠 Memory Context</h4>
              {memoryContext.map((item, idx) => (
                <div key={idx} style={{ 
                  fontSize: '0.85rem', 
                  padding: '0.3rem 0', 
                  borderBottom: '1px solid #2a2a3a' 
                }}>
                  <span style={{ color: '#6c63ff' }}>[{item.type}]</span> {item.text.slice(0, 150)}...
                </div>
              ))}
            </div>
          )}

          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            style={{ 
              minHeight: '400px', 
              fontFamily: 'monospace',
              fontSize: '0.95rem',
              padding: '1rem',
              resize: 'vertical'
            }}
            placeholder="Start writing your novel... The AI will remember everything!"
          />
        </div>

        <div className="flex gap-2">
          <button 
            className="btn btn-primary" 
            onClick={handleSave}
            disabled={isSaving}
          >
            {isSaving ? '💾 Saving...' : '💾 Save Novel'}
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={() => {
              if (window.confirm('Clear all content?')) {
                setContent('');
              }
            }}
          >
            Clear
          </button>
        </div>

        {novel?.id && (
          <div className="flex gap-4" style={{ fontSize: '0.85rem', color: '#6c63ff' }}>
            <span>📖 {chapters?.length || 0} chapters</span>
            <span>📝 {content.split(/\s+/).length} words</span>
            <span>🧠 {memoryContext.length} memory items</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default NovelEditor;