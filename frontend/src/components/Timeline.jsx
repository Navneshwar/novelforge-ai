import React, { useState, useEffect } from 'react';
import api from '../services/api';

const EVENT_TYPE_COLORS = {
  inciting: '#f59e0b',
  rising_action: '#6c63ff',
  climax: '#ef4444',
  falling_action: '#8b5cf6',
  resolution: '#10b981',
  default: '#38bdf8',
};

const EVENT_TYPE_LABELS = {
  inciting: 'Inciting Incident',
  rising_action: 'Rising Action',
  climax: 'Climax',
  falling_action: 'Falling Action',
  resolution: 'Resolution',
};

function Timeline({ novelId }) {
  const [plotPoints, setPlotPoints] = useState([]);
  const [chapters, setChapters] = useState([]);
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('vertical'); // vertical or horizontal
  const [expandedId, setExpandedId] = useState(null);
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    if (novelId) fetchTimelineData();
  }, [novelId]);

  const fetchTimelineData = async () => {
    try {
      setLoading(true);
      const [plotResp, novelResp, charResp] = await Promise.all([
        api.get(`/plots/${novelId}`),
        api.get(`/novels/${novelId}`),
        api.get(`/characters/${novelId}`).catch(() => ({ data: [] })),
      ]);

      setPlotPoints(plotResp.data || []);
      setChapters(novelResp.data?.chapters || []);
      setCharacters(charResp.data || []);
    } catch (err) {
      console.error('Failed to fetch timeline data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Build timeline events from plot points + character introductions
  const buildTimelineEvents = () => {
    const events = [];

    // Plot point events
    plotPoints.forEach(pp => {
      events.push({
        id: `plot_${pp.id}`,
        type: 'plot',
        eventType: pp.event_type || 'default',
        title: pp.title,
        description: pp.description,
        chapter: pp.chapter || 0,
        order: pp.timeline_order || 0,
        isMajor: pp.is_major,
        status: pp.status,
        importance: pp.importance || 0.5,
        involvedCharacters: pp.involved_characters || [],
        foreshadowing: pp.foreshadowing,
        resolution: pp.resolution,
      });
    });

    // Character introduction events
    characters.forEach(char => {
      if (char.first_appearance) {
        events.push({
          id: `char_intro_${char.id}`,
          type: 'character_intro',
          eventType: 'default',
          title: `${char.name} introduced`,
          description: char.description || `${char.name} makes their first appearance`,
          chapter: char.first_appearance,
          order: -1, // Before plot events
          isMajor: (char.importance_score || 0) > 0.7,
          characterName: char.name,
          characterRole: char.role,
        });
      }
    });

    // Sort by chapter then order
    events.sort((a, b) => {
      if (a.chapter !== b.chapter) return a.chapter - b.chapter;
      return a.order - b.order;
    });

    // Apply filter
    if (filterType !== 'all') {
      if (filterType === 'character_intro') {
        return events.filter(e => e.type === 'character_intro');
      }
      return events.filter(e => e.eventType === filterType || e.type === 'character_intro');
    }

    return events;
  };

  const timelineEvents = buildTimelineEvents();

  // Group events by chapter
  const groupedByChapter = {};
  timelineEvents.forEach(event => {
    const key = event.chapter || 0;
    if (!groupedByChapter[key]) groupedByChapter[key] = [];
    groupedByChapter[key].push(event);
  });

  const getChapterTitle = (num) => {
    const ch = chapters.find(c => (c.number || c.chapter_number) === num);
    return ch?.title || `Chapter ${num}`;
  };

  const getColor = (eventType) => EVENT_TYPE_COLORS[eventType] || EVENT_TYPE_COLORS.default;

  if (loading) {
    return (
      <div className="card" style={{ minHeight: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>📅 Loading timeline...</p>
      </div>
    );
  }

  return (
    <div className="timeline-container">
      {/* Header */}
      <div className="card" style={{ marginBottom: '1rem' }}>
        <div className="flex justify-between align-center" style={{ flexWrap: 'wrap', gap: '1rem' }}>
          <h3 style={{ margin: 0 }}>📅 Story Timeline</h3>
          <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
            {/* View mode toggle */}
            <button
              className={`btn ${viewMode === 'vertical' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('vertical')}
              style={{ fontSize: '0.8rem' }}
            >
              ↕ Vertical
            </button>
            <button
              className={`btn ${viewMode === 'horizontal' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setViewMode('horizontal')}
              style={{ fontSize: '0.8rem' }}
            >
              ↔ Horizontal
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mt-4" style={{ flexWrap: 'wrap' }}>
          <button
            className={`timeline-filter ${filterType === 'all' ? 'timeline-filter-active' : ''}`}
            onClick={() => setFilterType('all')}
          >
            All Events
          </button>
          {Object.entries(EVENT_TYPE_LABELS).map(([key, label]) => (
            <button
              key={key}
              className={`timeline-filter ${filterType === key ? 'timeline-filter-active' : ''}`}
              onClick={() => setFilterType(key)}
              style={{ borderColor: EVENT_TYPE_COLORS[key] }}
            >
              <span className="timeline-filter-dot" style={{ background: EVENT_TYPE_COLORS[key] }}></span>
              {label}
            </button>
          ))}
          <button
            className={`timeline-filter ${filterType === 'character_intro' ? 'timeline-filter-active' : ''}`}
            onClick={() => setFilterType('character_intro')}
          >
            👤 Characters
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="timeline-legend">
        {Object.entries(EVENT_TYPE_LABELS).map(([key, label]) => (
          <div key={key} className="timeline-legend-item">
            <span className="timeline-legend-dot" style={{ background: EVENT_TYPE_COLORS[key] }}></span>
            <span>{label}</span>
          </div>
        ))}
        <div className="timeline-legend-item">
          <span className="timeline-legend-dot" style={{ background: '#38bdf8' }}></span>
          <span>Character Intro</span>
        </div>
      </div>

      {/* Empty State */}
      {timelineEvents.length === 0 ? (
        <div className="card text-center" style={{ padding: '3rem' }}>
          <p style={{ fontSize: '3rem' }}>📅</p>
          <h3>No timeline events yet</h3>
          <p style={{ color: '#a0a0b8' }}>Add plot points and characters to build your story timeline.</p>
        </div>
      ) : viewMode === 'vertical' ? (
        /* ─── Vertical Timeline ───────────────────────────────── */
        <div className="timeline-vertical">
          {Object.entries(groupedByChapter)
            .sort(([a], [b]) => Number(a) - Number(b))
            .map(([chapterNum, events]) => (
              <div key={chapterNum} className="timeline-chapter-group">
                <div className="timeline-chapter-marker">
                  <div className="timeline-chapter-badge">
                    {getChapterTitle(Number(chapterNum))}
                  </div>
                </div>

                {events.map((event, idx) => (
                  <div
                    key={event.id}
                    className={`timeline-event ${event.isMajor ? 'timeline-event-major' : ''}`}
                    onClick={() => setExpandedId(expandedId === event.id ? null : event.id)}
                  >
                    <div className="timeline-event-line">
                      <div
                        className="timeline-event-dot"
                        style={{
                          background: getColor(event.eventType),
                          boxShadow: event.isMajor ? `0 0 12px ${getColor(event.eventType)}60` : 'none',
                          width: event.isMajor ? '16px' : '10px',
                          height: event.isMajor ? '16px' : '10px',
                        }}
                      />
                      {idx < events.length - 1 && <div className="timeline-connector" />}
                    </div>

                    <div className="timeline-event-content">
                      <div className="flex align-center gap-2" style={{ flexWrap: 'wrap' }}>
                        <h4 style={{ margin: 0, fontSize: '0.95rem' }}>
                          {event.type === 'character_intro' ? '👤 ' : ''}
                          {event.title}
                        </h4>
                        {event.isMajor && (
                          <span className="timeline-major-badge">★ Major</span>
                        )}
                        {event.eventType && event.eventType !== 'default' && (
                          <span
                            className="timeline-type-badge"
                            style={{ background: getColor(event.eventType) + '22', color: getColor(event.eventType) }}
                          >
                            {EVENT_TYPE_LABELS[event.eventType] || event.eventType}
                          </span>
                        )}
                      </div>

                      {event.description && (
                        <p style={{ fontSize: '0.85rem', marginTop: '0.3rem', color: '#a0a0b8' }}>
                          {expandedId === event.id ? event.description : event.description.slice(0, 120) + (event.description.length > 120 ? '...' : '')}
                        </p>
                      )}

                      {expandedId === event.id && (
                        <div className="timeline-event-details">
                          {event.status && (
                            <div className="timeline-detail-row">
                              <span>Status:</span>
                              <span style={{ textTransform: 'capitalize' }}>{event.status}</span>
                            </div>
                          )}
                          {event.foreshadowing && (
                            <div className="timeline-detail-row">
                              <span>Foreshadowing:</span>
                              <span>{event.foreshadowing}</span>
                            </div>
                          )}
                          {event.resolution && (
                            <div className="timeline-detail-row">
                              <span>Resolution:</span>
                              <span>{event.resolution}</span>
                            </div>
                          )}
                          {event.characterRole && (
                            <div className="timeline-detail-row">
                              <span>Role:</span>
                              <span style={{ textTransform: 'capitalize' }}>{event.characterRole}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ))}
        </div>
      ) : (
        /* ─── Horizontal Timeline ────────────────────────────── */
        <div className="timeline-horizontal-wrapper">
          <div className="timeline-horizontal">
            {Object.entries(groupedByChapter)
              .sort(([a], [b]) => Number(a) - Number(b))
              .map(([chapterNum, events]) => (
                <div key={chapterNum} className="timeline-h-chapter">
                  <div className="timeline-h-chapter-label">
                    {getChapterTitle(Number(chapterNum))}
                  </div>
                  <div className="timeline-h-events">
                    {events.map(event => (
                      <div
                        key={event.id}
                        className={`timeline-h-event ${expandedId === event.id ? 'timeline-h-event-expanded' : ''}`}
                        onClick={() => setExpandedId(expandedId === event.id ? null : event.id)}
                        style={{ borderColor: getColor(event.eventType) }}
                      >
                        <div
                          className="timeline-h-dot"
                          style={{ background: getColor(event.eventType) }}
                        />
                        <span className="timeline-h-title">{event.title}</span>
                        {expandedId === event.id && event.description && (
                          <p className="timeline-h-desc">{event.description}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Timeline;
