import React, { useState, useEffect } from 'react';
import api from '../services/api';

function NovelEditor({ novelId, novel, onUpdate }) {
  const [chapters, setChapters] = useState([]);
  const [currentChapter, setCurrentChapter] = useState(null);
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);
  const [autoSaveStatus, setAutoSaveStatus] = useState('');

  useEffect(() => {
    if (novel?.chapters) {
      setChapters(novel.chapters);
      if (novel.chapters.length > 0) {
        setCurrentChapter(novel.chapters[0]);
        setContent(novel.chapters[0].content || '');
      }
    }
  }, [novel]);

  const handleCreateChapter = async () => {
    if (!novelId) return;
    const newTitle = prompt('Chapter title:');
    if (!newTitle) return;

    try {
      const response = await api.post(`/novels/${novelId}/chapters`, {
        title: newTitle,
        content: ''
      });
      const newChapter = response.data;
      setChapters([...chapters, newChapter]);
      setCurrentChapter(newChapter);
      setContent('');
    } catch (err) {
      console.error('Failed to create chapter:', err);
    }
  };

  const handleSave = async () => {
    if (!novelId || !currentChapter) return;
    setSaving(true);
    try {
      await api.put(`/novels/${novelId}/chapters/${currentChapter.id}`, {
        content: content
      });
      setAutoSaveStatus('✓ Saved');
      setTimeout(() => setAutoSaveStatus(''), 2000);
      onUpdate?.();
    } catch (err) {
      setAutoSaveStatus('✗ Save failed');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleAIContinue = async () => {
    if (!novelId || !currentChapter) return;
    setSaving(true);
    try {
      const response = await api.post(`/novels/${novelId}/generate`, {
        chapter_id: currentChapter.id,
        context: content
      });
      setContent(content + '\n\n' + response.data.generated_text);
    } catch (err) {
      console.error('Failed to generate content:', err);
      alert('Failed to generate content');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="novel-editor-layout">
      {/* Chapter Sidebar */}
      <div className="chapter-sidebar">
        <div className="chapter-sidebar-header">
          <h3>Chapters</h3>
          <button className="btn btn-small btn-primary" onClick={handleCreateChapter} disabled={!novelId}>
            +
          </button>
        </div>

        <div className="chapter-list">
          {chapters.map((chapter) => (
            <div
              key={chapter.id}
              className={`chapter-item ${currentChapter?.id === chapter.id ? 'chapter-item-active' : ''}`}
              onClick={() => {
                setCurrentChapter(chapter);
                setContent(chapter.content || '');
              }}
            >
              <div className="chapter-item-info">
                <div className="chapter-item-title">{chapter.title}</div>
                <div className="chapter-item-words">{chapter.word_count || 0} words</div>
              </div>
            </div>
          ))}
        </div>

        <div className="chapter-sidebar-footer">
          <div className="chapter-stats">
            <div>Total: {chapters.length} chapters</div>
            <div>Words: {chapters.reduce((sum, ch) => sum + (ch.word_count || 0), 0)}</div>
          </div>
        </div>
      </div>

      {/* Editor Main */}
      <div className="editor-main">
        {currentChapter ? (
          <>
            <div className="editor-titlebar">
              <input
                type="text"
                className="editor-novel-title"
                value={currentChapter.title}
                onChange={(e) => setCurrentChapter({ ...currentChapter, title: e.target.value })}
                placeholder="Chapter Title"
              />
              <div className="editor-actions">
                <button className="btn btn-small btn-primary" onClick={handleAIContinue} disabled={saving || !novelId}>
                  {saving ? '⏳' : '✨'} AI Continue
                </button>
                <button className="btn btn-small btn-secondary" onClick={handleSave} disabled={saving || !novelId}>
                  {saving ? 'Saving...' : '💾'} Save
                </button>
                {autoSaveStatus && <span className="save-status">{autoSaveStatus}</span>}
              </div>
            </div>

            <div className="editor-toolbar">
              <button className="toolbar-btn" title="Bold"><strong>B</strong></button>
              <button className="toolbar-btn" title="Italic"><em>I</em></button>
              <button className="toolbar-btn" title="Underline"><u>U</u></button>
              <button className="toolbar-btn" title="Heading">H1</button>
              <button className="toolbar-btn" title="Quote">"</button>
            </div>

            <div className="rich-editor-wrapper">
              <div className="rich-editor-body">
                <textarea
                  className="rich-editor-content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Start writing your story..."
                />
              </div>
              <div className="rich-editor-statusbar">
                <span>Words: {content.split(/\s+/).filter(w => w.length > 0).length}</span>
                <span>Characters: {content.length}</span>
              </div>
            </div>
          </>
        ) : (
          <div className="empty-state" style={{ margin: 'var(--spacing-xl)' }}>
            <div className="empty-state-icon">📝</div>
            <h3>No chapters yet</h3>
            <p>Create your first chapter to start writing</p>
            <button className="btn btn-primary" onClick={handleCreateChapter} disabled={!novelId}>
              Create Chapter
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default NovelEditor;
