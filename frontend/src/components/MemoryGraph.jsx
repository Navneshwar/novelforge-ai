import React, { useState, useEffect, useMemo } from 'react';
import api from '../services/api';

const TYPE_META = {
  novel: { label: 'Novel', color: '#4F46E5', icon: '📖' },
  character: { label: 'Character', color: '#0EA5E9', icon: '👤' },
  chapter: { label: 'Chapter', color: '#10B981', icon: '📑' },
  plot: { label: 'Plot Point', color: '#F59E0B', icon: '📌' },
  location: { label: 'Location', color: '#8B5CF6', icon: '📍' },
  event: { label: 'Event', color: '#EC4899', icon: '⚡' },
  concept: { label: 'Concept', color: '#64748B', icon: '💡' },
};

const FALLBACK_COLORS = ['#4F46E5', '#0EA5E9', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#64748B', '#DC2626'];

function getTypeMeta(type, order) {
  if (TYPE_META[type]) return TYPE_META[type];
  const color = FALLBACK_COLORS[order % FALLBACK_COLORS.length];
  return { label: (type || 'unknown').replace(/_/g, ' '), color, icon: '🔹' };
}

function MemoryGraph({ novelId, novel }) {
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aiMemoryLoaded, setAiMemoryLoaded] = useState(false);
  const [loadingAiMemory, setLoadingAiMemory] = useState(false);
  const [aiMemoryError, setAiMemoryError] = useState(null);

  const [search, setSearch] = useState('');
  const [activeTypes, setActiveTypes] = useState(null); // null = all
  const [originFilter, setOriginFilter] = useState('all'); // all | database | cognee
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  useEffect(() => {
    if (novelId) {
      fetchMemoryData();
    } else {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [novelId]);

  // Fast path: structural data only (characters/chapters/plot points),
  // pure SQL — loads near-instantly.
  const fetchMemoryData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get(`/memory/graph/${novelId}`);
      const data = response.data || {};
      setGraph({
        nodes: Array.isArray(data.nodes) ? data.nodes : [],
        edges: Array.isArray(data.edges) ? data.edges : [],
      });
    } catch (err) {
      console.error('Failed to fetch memory graph:', err);
      setError('Failed to load the memory graph.');
    } finally {
      setLoading(false);
    }
  };

  // Slow path: also pulls Cognee's AI-extracted entities/relationships,
  // which requires a local LLM round-trip. Opt-in only, triggered by a
  // button, so the tab never blocks on it by default.
  const loadAiMemory = async () => {
    try {
      setLoadingAiMemory(true);
      setAiMemoryError(null);
      const response = await api.get(`/memory/graph/${novelId}`, {
        params: { include_ai_memory: true },
      });
      const data = response.data || {};
      setGraph({
        nodes: Array.isArray(data.nodes) ? data.nodes : [],
        edges: Array.isArray(data.edges) ? data.edges : [],
      });
      setAiMemoryLoaded(true);
    } catch (err) {
      console.error('Failed to load AI memory:', err);
      setAiMemoryError('AI memory took too long or failed to load. Your structural graph is still shown below.');
    } finally {
      setLoadingAiMemory(false);
    }
  };

  // Distinct node types present in this graph, in first-seen order, with a
  // stable color/icon assigned to each (known types get curated colors,
  // anything else falls back to a rotating palette).
  const typeList = useMemo(() => {
    const seen = [];
    graph.nodes.forEach((n) => {
      const t = n.type || 'unknown';
      if (!seen.includes(t)) seen.push(t);
    });
    return seen.map((t, i) => ({ type: t, ...getTypeMeta(t, i) }));
  }, [graph.nodes]);

  const typeMetaMap = useMemo(() => {
    const map = {};
    typeList.forEach((t) => { map[t.type] = t; });
    return map;
  }, [typeList]);

  const effectiveActiveTypes = activeTypes || new Set(typeList.map((t) => t.type));

  const toggleType = (type) => {
    setActiveTypes((prev) => {
      const base = prev || new Set(typeList.map((t) => t.type));
      const next = new Set(base);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  };

  const resetFilters = () => {
    setSearch('');
    setActiveTypes(null);
    setOriginFilter('all');
  };

  const filteredNodes = useMemo(() => {
    const q = search.trim().toLowerCase();
    return graph.nodes.filter((n) => {
      const type = n.type || 'unknown';
      if (!effectiveActiveTypes.has(type)) return false;
      if (originFilter !== 'all' && (n.origin || 'database') !== originFilter) return false;
      if (q && !(n.label || '').toLowerCase().includes(q)) return false;
      return true;
    });
  }, [graph.nodes, effectiveActiveTypes, originFilter, search]);

  const visibleNodeIds = useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes]);

  const filteredEdges = useMemo(() => (
    graph.edges.filter((e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target))
  ), [graph.edges, visibleNodeIds]);

  const nodesById = useMemo(() => {
    const map = {};
    graph.nodes.forEach((n) => { map[n.id] = n; });
    return map;
  }, [graph.nodes]);

  const connectionsForNode = (nodeId) => {
    const outgoing = graph.edges.filter((e) => e.source === nodeId);
    const incoming = graph.edges.filter((e) => e.target === nodeId);
    return { outgoing, incoming };
  };

  const selectedNode = selectedNodeId ? nodesById[selectedNodeId] : null;
  const selectedConnections = selectedNodeId ? connectionsForNode(selectedNodeId) : null;

  if (!novelId) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🧠</div>
        <h3>Save your novel first</h3>
        <p>Create and save your novel to visualize the memory graph</p>
      </div>
    );
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 'var(--spacing-xl)' }}>Loading memory graph...</div>;
  }

  return (
    <div className="memory-graph-panel">
      <div style={{ marginBottom: 'var(--spacing-md)' }}>
        <h2>Memory Graph</h2>
        <p>Explore the entities and relationships NovelForge remembers about your story</p>
      </div>

      {error && (
        <div className="card" style={{ borderColor: 'var(--secondary-coral)', background: 'rgba(220, 38, 38, 0.05)' }}>
          <p style={{ color: 'var(--secondary-coral)' }}>⚠️ {error}</p>
        </div>
      )}

      {/* Stats */}
      <div className="grid-2">
        <div className="card">
          <h4>Nodes</h4>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary-coral)' }}>
            {filteredNodes.length}{filteredNodes.length !== graph.nodes.length ? ` / ${graph.nodes.length}` : ''}
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>Story elements tracked</p>
        </div>
        <div className="card">
          <h4>Connections</h4>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary-coral)' }}>
            {filteredEdges.length}{filteredEdges.length !== graph.edges.length ? ` / ${graph.edges.length}` : ''}
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>Relationships found</p>
        </div>
      </div>

      {graph.nodes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🧠</div>
          <h3>Nothing remembered yet</h3>
          <p>Write a few chapters and add characters — NovelForge will start building a memory graph automatically.</p>
        </div>
      ) : (
        <>
          {/* AI memory (opt-in, slower) */}
          <div className="card mg-ai-banner">
            <div className="mg-ai-banner-text">
              <strong>🧠 AI-extracted memory</strong>
              <p style={{ margin: 0 }}>
                {aiMemoryLoaded
                  ? 'Loaded — entities Cognee extracted from your chapters are now included below.'
                  : 'The graph below is your structural data (fast). Load Cognee\'s AI-extracted entities and relationships too — this runs a local LLM query, so it can take up to 30-40 seconds.'}
              </p>
              {aiMemoryError && <p style={{ color: 'var(--secondary-coral)', margin: '0.4rem 0 0' }}>{aiMemoryError}</p>}
            </div>
            <button
              className="btn btn-secondary btn-small"
              onClick={loadAiMemory}
              disabled={loadingAiMemory || aiMemoryLoaded}
            >
              {loadingAiMemory ? '⏳ Thinking...' : aiMemoryLoaded ? '✓ Loaded' : 'Load AI Memory'}
            </button>
          </div>

          {/* Filters */}
          <div className="card mg-filters">
            <div className="mg-filters-row">
              <input
                type="text"
                placeholder="🔍 Search nodes by name..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="mg-search-input"
              />
              <div className="mg-origin-toggle">
                {[
                  { key: 'all', label: 'All sources' },
                  { key: 'database', label: '🗂️ App data' },
                  { key: 'cognee', label: '🧠 AI memory' },
                ].map((opt) => (
                  <button
                    key={opt.key}
                    className={`mg-origin-btn ${originFilter === opt.key ? 'active' : ''}`}
                    onClick={() => setOriginFilter(opt.key)}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
              <button className="btn btn-secondary btn-small" onClick={resetFilters}>
                Reset filters
              </button>
            </div>

            <div className="mg-type-filters">
              {typeList.map(({ type, label, color, icon }) => {
                const isActive = effectiveActiveTypes.has(type);
                const count = graph.nodes.filter((n) => (n.type || 'unknown') === type).length;
                return (
                  <button
                    key={type}
                    className={`mg-type-chip ${isActive ? 'active' : ''}`}
                    style={{ '--chip-color': color }}
                    onClick={() => toggleType(type)}
                    title={isActive ? `Hide ${label}` : `Show ${label}`}
                  >
                    <span className="mg-chip-dot" style={{ background: color }} />
                    {icon} {label} <span className="mg-chip-count">{count}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mg-explorer">
            {/* Node list */}
            <div className="card mg-node-list">
              <h4 style={{ marginBottom: 'var(--spacing-sm)' }}>
                Nodes {filteredNodes.length > 0 && `(${filteredNodes.length})`}
              </h4>
              {filteredNodes.length === 0 ? (
                <p style={{ color: 'var(--text-light)' }}>No nodes match your filters.</p>
              ) : (
                <div className="mg-node-items">
                  {filteredNodes.map((node) => {
                    const meta = typeMetaMap[node.type || 'unknown'] || getTypeMeta(node.type, 0);
                    const connCount = graph.edges.filter((e) => e.source === node.id || e.target === node.id).length;
                    return (
                      <div
                        key={node.id}
                        className={`mg-node-item ${selectedNodeId === node.id ? 'selected' : ''}`}
                        style={{ '--chip-color': meta.color }}
                        onClick={() => setSelectedNodeId(node.id === selectedNodeId ? null : node.id)}
                      >
                        <span className="mg-node-dot" style={{ background: meta.color }} />
                        <div className="mg-node-info">
                          <span className="mg-node-label">{node.label}</span>
                          <span className="mg-node-sub">{meta.icon} {meta.label} · {connCount} link{connCount !== 1 ? 's' : ''}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Connection detail */}
            <div className="card mg-node-detail">
              {selectedNode ? (
                <>
                  <div style={{ display: 'flex', gap: 'var(--spacing-sm)', alignItems: 'center', marginBottom: 'var(--spacing-sm)' }}>
                    <span
                      className="mg-node-dot"
                      style={{ background: (typeMetaMap[selectedNode.type] || {}).color || '#64748B' }}
                    />
                    <h3 style={{ margin: 0 }}>{selectedNode.label}</h3>
                  </div>
                  <span className="badge badge-primary" style={{ marginBottom: 'var(--spacing-md)' }}>
                    {(typeMetaMap[selectedNode.type] || {}).label || selectedNode.type}
                  </span>

                  {selectedNode.data?.description && (
                    <p style={{ marginBottom: 'var(--spacing-md)' }}>{selectedNode.data.description}</p>
                  )}

                  <h4 style={{ fontSize: '0.9rem', marginBottom: 'var(--spacing-sm)' }}>
                    Connections ({selectedConnections.outgoing.length + selectedConnections.incoming.length})
                  </h4>
                  {selectedConnections.outgoing.length + selectedConnections.incoming.length === 0 ? (
                    <p style={{ color: 'var(--text-light)' }}>No connections found for this node.</p>
                  ) : (
                    <div className="mg-connection-list">
                      {selectedConnections.outgoing.map((e, idx) => {
                        const target = nodesById[e.target];
                        if (!target) return null;
                        return (
                          <div key={`out-${idx}`} className="mg-connection-item">
                            <span className="mg-conn-rel">→ {(e.type || 'related to').replace(/_/g, ' ')}</span>
                            <button className="mg-conn-target" onClick={() => setSelectedNodeId(target.id)}>
                              {target.label}
                            </button>
                          </div>
                        );
                      })}
                      {selectedConnections.incoming.map((e, idx) => {
                        const source = nodesById[e.source];
                        if (!source) return null;
                        return (
                          <div key={`in-${idx}`} className="mg-connection-item">
                            <span className="mg-conn-rel">← {(e.type || 'related to').replace(/_/g, ' ')}</span>
                            <button className="mg-conn-target" onClick={() => setSelectedNodeId(source.id)}>
                              {source.label}
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </>
              ) : (
                <div className="mg-detail-placeholder">
                  <div className="empty-state-icon">👈</div>
                  <p>Select a node from the list to see its details and connections.</p>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default MemoryGraph;
