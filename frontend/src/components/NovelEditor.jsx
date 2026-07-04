import React, { useState, useEffect, useCallback } from 'react';
import RichTextEditor from './RichTextEditor';
import api from '../services/api';
import { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak } from 'docx';
import { saveAs } from 'file-saver';

function NovelEditor({ novel, onSave }) {
  const [title, setTitle] = useState(novel?.title || '');
  const [genre, setGenre] = useState(novel?.genre || 'General');
  const [chapters, setChapters] = useState([]);
  const [activeChapterIdx, setActiveChapterIdx] = useState(0);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [memoryContext, setMemoryContext] = useState([]);
  const [showMemory, setShowMemory] = useState(false);

  // Initialize chapters from novel data
  useEffect(() => {
    if (novel?.chapters && novel.chapters.length > 0) {
      const sorted = [...novel.chapters].sort((a, b) => (a.number || a.chapter_number || 0) - (b.number || b.chapter_number || 0));
      setChapters(sorted.map(ch => ({
        id: ch.id,
        title: ch.title || `Chapter ${ch.number || ch.chapter_number}`,
        content: ch.content || '',
        chapter_number: ch.number || ch.chapter_number,
        summary: ch.summary || '',
        status: ch.status || 'draft',
        word_count: ch.word_count || 0,
      })));
    } else {
      // Start with one empty chapter
      setChapters([{
        id: null,
        title: 'Chapter 1',
        content: '',
        chapter_number: 1,
        summary: '',
        status: 'draft',
        word_count: 0,
      }]);
    }
    setTitle(novel?.title || '');
    setGenre(novel?.genre || 'General');
  }, [novel?.id]);

  useEffect(() => {
    if (novel?.id) {
      fetchMemoryContext();
    }
  }, [novel?.id]);

  const fetchMemoryContext = async () => {
    try {
      const currentContent = chapters[activeChapterIdx]?.content || '';
      const queryText = currentContent.replace(/<[^>]*>/g, '').slice(-500) || 'story context';
      const response = await api.post(`/memory/recall/${novel.id}`, {
        query: queryText,
        limit: 5
      });
      setMemoryContext(response.data.items || []);
    } catch (err) {
      console.error('Failed to fetch memory context:', err);
    }
  };

  const activeChapter = chapters[activeChapterIdx] || null;

  const updateChapterContent = useCallback((html) => {
    setChapters(prev => {
      const updated = [...prev];
      if (updated[activeChapterIdx]) {
        updated[activeChapterIdx] = {
          ...updated[activeChapterIdx],
          content: html,
          word_count: html.replace(/<[^>]*>/g, '').split(/\s+/).filter(Boolean).length,
        };
      }
      return updated;
    });
  }, [activeChapterIdx]);

  const updateChapterTitle = (idx, newTitle) => {
    setChapters(prev => {
      const updated = [...prev];
      updated[idx] = { ...updated[idx], title: newTitle };
      return updated;
    });
  };

  const addChapter = () => {
    const newNum = chapters.length + 1;
    setChapters(prev => [...prev, {
      id: null,
      title: `Chapter ${newNum}`,
      content: '',
      chapter_number: newNum,
      summary: '',
      status: 'draft',
      word_count: 0,
    }]);
    setActiveChapterIdx(chapters.length);
  };

  const deleteChapter = async (idx) => {
    if (chapters.length <= 1) return;
    if (!window.confirm(`Delete "${chapters[idx].title}"?`)) return;

    const ch = chapters[idx];

    // Delete from backend if it has an ID
    if (ch.id && novel?.id) {
      try {
        await api.delete(`/novels/${novel.id}/chapters/${ch.id}`);
      } catch (err) {
        console.error('Failed to delete chapter from server:', err);
      }
    }

    const updated = chapters.filter((_, i) => i !== idx).map((c, i) => ({
      ...c,
      chapter_number: i + 1,
    }));
    setChapters(updated);
    setActiveChapterIdx(Math.min(activeChapterIdx, updated.length - 1));
  };

  const handleSave = async () => {
    if (!novel?.id && novel?.id !== undefined) {
      // New novel flow
      setIsSaving(true);
      setSaveStatus('Saving...');
      try {
        const allContent = chapters.map(ch =>
          ch.content.replace(/<[^>]*>/g, '')
        ).join('\n\n');

        await onSave({
          title,
          genre,
          content: allContent,
          chapters: chapters.map(ch => ({
            id: ch.id || undefined,
            title: ch.title,
            content: ch.content,
            chapter_number: ch.chapter_number,
            summary: ch.summary,
            status: ch.status,
          })),
        });
        setSaveStatus('✅ Saved!');
      } catch (err) {
        setSaveStatus('❌ Save failed');
      } finally {
        setIsSaving(false);
        setTimeout(() => setSaveStatus(''), 3000);
      }
      return;
    }

    setIsSaving(true);
    setSaveStatus('Saving...');
    try {
      // Save each chapter individually
      for (const ch of chapters) {
        if (ch.id) {
          await api.put(`/novels/${novel.id}/chapters/${ch.id}`, {
            title: ch.title,
            content: ch.content,
            summary: ch.summary,
            status: ch.status,
          });
        } else {
          const resp = await api.post(`/novels/${novel.id}/chapters`, {
            title: ch.title,
            content: ch.content,
            chapter_number: ch.chapter_number,
            summary: ch.summary,
          });
          ch.id = resp.data.id;
        }
      }

      // Save novel metadata + aggregate content
      const allContent = chapters.map(ch =>
        ch.content.replace(/<[^>]*>/g, '')
      ).join('\n\n');

      await api.put(`/novels/${novel.id}`, {
        title,
        genre,
        content: allContent,
      });

      setSaveStatus('✅ Saved!');
      await fetchMemoryContext();
    } catch (err) {
      setSaveStatus('❌ Save failed');
      console.error('Save error:', err);
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveStatus(''), 3000);
    }
  };

  const handleAIWrite = async () => {
    const currentContent = activeChapter?.content || '';
    const plainText = currentContent.replace(/<[^>]*>/g, '');
    if (!plainText.trim()) {
      alert('Please write some content first to continue from.');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await api.post(`/memory/recall/${novel.id}`, {
        query: plainText.slice(-300),
        limit: 3
      });

      const context = (response.data.items || []).map(item => item.text).join('\n');

      const generateResponse = await api.post(`/novels/${novel.id}/generate`, {
        prompt: plainText,
        context: context,
        style: 'continue'
      });

      const newContent = currentContent + '<p>' + generateResponse.data.generated_text + '</p>';
      updateChapterContent(newContent);
    } catch (err) {
      alert('Failed to generate content');
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  // ── Export Functions ────────────────────────────────────────────

  const stripHtml = (html) => {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
  };

  const exportToDocx = async () => {
    const children = [];

    // Title page
    children.push(
      new Paragraph({
        text: title || 'Untitled Novel',
        heading: HeadingLevel.TITLE,
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
      }),
      new Paragraph({
        text: genre || 'General',
        alignment: AlignmentType.CENTER,
        spacing: { after: 800 },
        children: [
          new TextRun({ text: genre || 'General', italics: true, size: 24, color: '666666' }),
        ],
      }),
      new Paragraph({
        children: [new PageBreak()],
      })
    );

    // Chapters
    chapters.forEach((ch) => {
      children.push(
        new Paragraph({
          text: ch.title || `Chapter ${ch.chapter_number}`,
          heading: HeadingLevel.HEADING_1,
          spacing: { before: 400, after: 200 },
          pageBreakBefore: true,
        })
      );

      const plainText = stripHtml(ch.content);
      const paragraphs = plainText.split('\n').filter(p => p.trim());
      paragraphs.forEach(para => {
        children.push(
          new Paragraph({
            text: para.trim(),
            spacing: { after: 120 },
            children: [
              new TextRun({ text: para.trim(), size: 24 }),
            ],
          })
        );
      });
    });

    const doc = new Document({
      sections: [{
        properties: {},
        children,
      }],
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, `${(title || 'novel').replace(/[^a-zA-Z0-9]/g, '_')}.docx`);
  };

  const exportToTxt = () => {
    let text = `${title || 'Untitled Novel'}\n${'='.repeat(50)}\n\n`;
    chapters.forEach(ch => {
      text += `\n${'─'.repeat(40)}\n`;
      text += `${ch.title || `Chapter ${ch.chapter_number}`}\n`;
      text += `${'─'.repeat(40)}\n\n`;
      text += stripHtml(ch.content) + '\n\n';
    });

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    saveAs(blob, `${(title || 'novel').replace(/[^a-zA-Z0-9]/g, '_')}.txt`);
  };

  // ── Stats ──────────────────────────────────────────────────────

  const totalWords = chapters.reduce((sum, ch) => sum + (ch.word_count || 0), 0);

  return (
    <div className="novel-editor-layout">
      {/* Chapter Sidebar */}
      <div className="chapter-sidebar">
        <div className="chapter-sidebar-header">
          <h4 style={{ margin: 0 }}>📑 Chapters</h4>
          <button
            className="btn btn-primary"
            onClick={addChapter}
            style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
          >
            + Add
          </button>
        </div>

        <div className="chapter-list">
          {chapters.map((ch, idx) => (
            <div
              key={idx}
              className={`chapter-item ${idx === activeChapterIdx ? 'chapter-item-active' : ''}`}
              onClick={() => setActiveChapterIdx(idx)}
            >
              <div className="chapter-item-info">
                <span className="chapter-item-title">{ch.title}</span>
                <span className="chapter-item-words">{ch.word_count || 0} words</span>
              </div>
              {chapters.length > 1 && (
                <button
                  className="chapter-delete-btn"
                  onClick={(e) => { e.stopPropagation(); deleteChapter(idx); }}
                  title="Delete chapter"
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="chapter-sidebar-footer">
          <div className="chapter-stats">
            <span>📝 {totalWords} total words</span>
            <span>📑 {chapters.length} chapters</span>
          </div>
        </div>
      </div>

      {/* Main Editor Area */}
      <div className="editor-main">
        {/* Novel Title Bar */}
        <div className="editor-titlebar">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Novel Title"
            className="editor-novel-title"
          />
          <div className="editor-actions">
            <button
              className="btn btn-secondary"
              onClick={() => setShowMemory(!showMemory)}
              style={{ fontSize: '0.8rem' }}
            >
              {showMemory ? '🧠 Hide Memory' : '🧠 Memory'}
            </button>
            {novel?.id && (
              <button
                className="btn btn-secondary"
                onClick={handleAIWrite}
                disabled={isGenerating}
                style={{ fontSize: '0.8rem' }}
              >
                {isGenerating ? '✍️ Writing...' : '✍️ AI Continue'}
              </button>
            )}
            <div className="export-dropdown">
              <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }}>
                📄 Export ▾
              </button>
              <div className="export-dropdown-content">
                <button onClick={exportToDocx}>📄 Export as DOCX</button>
                <button onClick={exportToTxt}>📝 Export as TXT</button>
              </div>
            </div>
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={isSaving}
              style={{ fontSize: '0.8rem' }}
            >
              {isSaving ? '💾 Saving...' : '💾 Save'}
            </button>
            {saveStatus && (
              <span className="save-status">{saveStatus}</span>
            )}
          </div>
        </div>

        {/* Memory Context Panel */}
        {showMemory && memoryContext.length > 0 && (
          <div className="memory-panel">
            <h4 style={{ fontSize: '0.9rem', marginBottom: '0.5rem', color: '#a855f7' }}>🧠 Memory Context</h4>
            {memoryContext.map((item, idx) => (
              <div key={idx} className="memory-item">
                <span style={{ color: '#6c63ff', fontWeight: 600 }}>[{item.type}]</span>{' '}
                {item.text?.slice(0, 150)}...
              </div>
            ))}
          </div>
        )}

        {/* Chapter Title */}
        {activeChapter && (
          <div className="chapter-title-bar">
            <input
              type="text"
              value={activeChapter.title}
              onChange={(e) => updateChapterTitle(activeChapterIdx, e.target.value)}
              className="chapter-title-input"
              placeholder="Chapter title..."
            />
          </div>
        )}

        {/* Rich Text Editor */}
        {activeChapter && (
          <RichTextEditor
            key={`chapter-${activeChapterIdx}-${activeChapter.id || 'new'}`}
            content={activeChapter.content}
            onUpdate={updateChapterContent}
            placeholder="Start writing this chapter..."
          />
        )}
      </div>
    </div>
  );
}

export default NovelEditor;