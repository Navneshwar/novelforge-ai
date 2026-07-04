import React, { useState, useEffect } from 'react';
import api from '../services/api';

function MemoryGraph({ novelId, novel }) {
  const [memoryData, setMemoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    if (novelId) {
      fetchMemoryData();
    } else {
      setLoading(false);
    }
  }, [novelId]);

  const fetchMemoryData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/novels/${novelId}/memory/graph`);
      setMemoryData(response.data);
    } catch (err) {
      console.error('Failed to fetch memory graph:', err);
    } finally {
      setLoading(false);
    }
  };

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
      <div style={{ marginBottom: 'var(--spacing-lg)' }}>
        <h2>Memory Graph</h2>
        <p>Interactive visualization of your story's knowledge network</p>
      </div>

      <div className="grid-2" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <div className="card">
          <h4>Nodes</h4>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary-coral)' }}>
            {memoryData?.nodes_count || 0}
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>Story elements tracked</p>
        </div>
        <div className="card">
          <h4>Connections</h4>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary-coral)' }}>
            {memoryData?.edges_count || 0}
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-light)' }}>Relationships found</p>
        </div>
      </div>

      <div className="card" style={{ minHeight: '400px' }}>
        <p style={{ textAlign: 'center', color: 'var(--text-light)', padding: 'var(--spacing-xl)' }}>
          📊 3D Memory Graph Visualization
          <br />
          (Interactive Three.js visualization coming soon)
        </p>
      </div>

      {selectedNode && (
        <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
          <h3>{selectedNode.name}</h3>
          <div style={{ display: 'flex', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-md)' }}>
            <span className="badge badge-primary">{selectedNode.type}</span>
          </div>
          <p>{selectedNode.description}</p>
        </div>
      )}
    </div>
  );
}

export default MemoryGraph;
