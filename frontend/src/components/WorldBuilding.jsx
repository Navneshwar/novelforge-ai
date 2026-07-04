import React, { useState, useEffect } from 'react';
import api from '../services/api';

const CATEGORIES = [
  { key: 'location', icon: '📍', label: 'Locations', description: 'Places, cities, realms, and landmarks' },
  { key: 'lore', icon: '📜', label: 'Lore & History', description: 'Historical events, legends, and world history' },
  { key: 'magic', icon: '✨', label: 'Magic / Technology', description: 'Magic systems, tech, rules, and limitations' },
  { key: 'culture', icon: '🏛️', label: 'Cultures & Factions', description: 'Societies, organizations, beliefs, and customs' },
  { key: 'fauna', icon: '🐉', label: 'Flora & Fauna', description: 'Creatures, plants, and unique species' },
];

const CATEGORY_FIELDS = {
  location: ['terrain', 'climate', 'population', 'significance'],
  lore: ['era', 'significance', 'source'],
  magic: ['type', 'source', 'limitations', 'cost'],
  culture: ['beliefs', 'customs', 'allies', 'enemies'],
  fauna: ['habitat', 'behavior', 'danger_level', 'rarity'],
};

function WorldBuilding({ novelId }) {
  const [elements, setElements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('location');
  const [showForm, setShowForm] = useState(false);
  const [editingElement, setEditingElement] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  // Form state
  const [formName, setFormName] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formProperties, setFormProperties] = useState({});
  const [formConnections, setFormConnections] = useState('');
  const [formTags, setFormTags] = useState('');
  const [formNotes, setFormNotes] = useState('');

  useEffect(() => {
    if (novelId) fetchElements();
  }, [novelId]);

  const fetchElements = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/world/${novelId}`);
      setElements(response.data || []);
    } catch (err) {
      console.error('Failed to fetch world elements:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredElements = elements.filter(el => el.category === activeCategory);

  const resetForm = () => {
    setFormName('');
    setFormDescription('');
    setFormProperties({});
    setFormConnections('');
    setFormTags('');
    setFormNotes('');
    setEditingElement(null);
  };

  const openAddForm = () => {
    resetForm();
    setShowForm(true);
  };

  const openEditForm = (el) => {
    setEditingElement(el);
    setFormName(el.name);
    setFormDescription(el.description || '');
    setFormProperties(el.properties || {});
    setFormConnections((el.connections || []).join(', '));
    setFormTags((el.tags || []).join(', '));
    setFormNotes(el.notes || '');
    setShowForm(true);
  };

  const handleSave = async () => {
    if (!formName.trim()) return;

    const data = {
      category: activeCategory,
      name: formName.trim(),
      description: formDescription.trim(),
      properties: formProperties,
      connections: formConnections.split(',').map(s => s.trim()).filter(Boolean),
      tags: formTags.split(',').map(s => s.trim()).filter(Boolean),
      notes: formNotes.trim(),
    };

    try {
      if (editingElement) {
        await api.put(`/world/${novelId}/${editingElement.id}`, data);
      } else {
        await api.post(`/world/${novelId}`, data);
      }
      await fetchElements();
      setShowForm(false);
      resetForm();
    } catch (err) {
      alert('Failed to save element');
      console.error(err);
    }
  };

  const handleDelete = async (elementId) => {
    if (!window.confirm('Delete this element?')) return;
    try {
      await api.delete(`/world/${novelId}/${elementId}`);
      setElements(elements.filter(el => el.id !== elementId));
    } catch (err) {
      alert('Failed to delete element');
      console.error(err);
    }
  };

  const updateProperty = (key, value) => {
    setFormProperties(prev => ({ ...prev, [key]: value }));
  };

  const catInfo = CATEGORIES.find(c => c.key === activeCategory);
  const fields = CATEGORY_FIELDS[activeCategory] || [];

  if (loading) {
    return (
      <div className="card" style={{ minHeight: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>🌍 Loading world data...</p>
      </div>
    );
  }

  return (
    <div className="worldbuilding-container">
      {/* Category Tabs */}
      <div className="wb-category-tabs">
        {CATEGORIES.map(cat => (
          <button
            key={cat.key}
            className={`wb-category-tab ${activeCategory === cat.key ? 'wb-category-tab-active' : ''}`}
            onClick={() => { setActiveCategory(cat.key); setShowForm(false); }}
          >
            <span className="wb-tab-icon">{cat.icon}</span>
            <span className="wb-tab-label">{cat.label}</span>
            <span className="wb-tab-count">
              {elements.filter(el => el.category === cat.key).length}
            </span>
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="card" style={{ marginTop: '1rem' }}>
        <div className="flex justify-between align-center mb-4">
          <div>
            <h3 style={{ margin: 0 }}>{catInfo?.icon} {catInfo?.label}</h3>
            <p style={{ fontSize: '0.85rem', margin: '0.25rem 0 0 0' }}>{catInfo?.description}</p>
          </div>
          <button className="btn btn-primary" onClick={openAddForm} style={{ fontSize: '0.85rem' }}>
            + Add {catInfo?.label?.replace(/s$/, '') || 'Element'}
          </button>
        </div>

        {/* Add/Edit Form */}
        {showForm && (
          <div className="wb-form" style={{ marginBottom: '1.5rem' }}>
            <div className="flex gap-4" style={{ flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <label>Name *</label>
                <input
                  type="text"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  placeholder={`${catInfo?.label?.replace(/s$/, '')} name...`}
                  autoFocus
                />
              </div>
              <div style={{ flex: 2, minWidth: '300px' }}>
                <label>Description</label>
                <textarea
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  placeholder="Describe this element..."
                  rows={2}
                  style={{ resize: 'vertical' }}
                />
              </div>
            </div>

            {/* Category-specific properties */}
            <div className="wb-properties-grid" style={{ marginTop: '0.75rem' }}>
              {fields.map(field => (
                <div key={field}>
                  <label style={{ textTransform: 'capitalize' }}>{field.replace(/_/g, ' ')}</label>
                  <input
                    type="text"
                    value={formProperties[field] || ''}
                    onChange={(e) => updateProperty(field, e.target.value)}
                    placeholder={`Enter ${field.replace(/_/g, ' ')}...`}
                  />
                </div>
              ))}
            </div>

            <div className="flex gap-4" style={{ marginTop: '0.75rem', flexWrap: 'wrap' }}>
              <div style={{ flex: 1 }}>
                <label>Connections (comma-separated)</label>
                <input
                  type="text"
                  value={formConnections}
                  onChange={(e) => setFormConnections(e.target.value)}
                  placeholder="e.g., Castle Ironholm, Elven Forest..."
                />
              </div>
              <div style={{ flex: 1 }}>
                <label>Tags (comma-separated)</label>
                <input
                  type="text"
                  value={formTags}
                  onChange={(e) => setFormTags(e.target.value)}
                  placeholder="e.g., dangerous, ancient, sacred..."
                />
              </div>
            </div>

            <div style={{ marginTop: '0.75rem' }}>
              <label>Notes</label>
              <textarea
                value={formNotes}
                onChange={(e) => setFormNotes(e.target.value)}
                placeholder="Additional notes..."
                rows={2}
                style={{ resize: 'vertical' }}
              />
            </div>

            <div className="flex gap-2" style={{ marginTop: '1rem' }}>
              <button className="btn btn-primary" onClick={handleSave} style={{ fontSize: '0.85rem' }}>
                {editingElement ? '✅ Update' : '✅ Save'}
              </button>
              <button className="btn btn-secondary" onClick={() => { setShowForm(false); resetForm(); }} style={{ fontSize: '0.85rem' }}>
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Elements List */}
        {filteredElements.length === 0 && !showForm ? (
          <div className="text-center" style={{ padding: '2rem' }}>
            <p style={{ fontSize: '3rem' }}>{catInfo?.icon}</p>
            <p>No {catInfo?.label?.toLowerCase()} added yet.</p>
            <button className="btn btn-primary mt-4" onClick={openAddForm} style={{ fontSize: '0.85rem' }}>
              + Add Your First {catInfo?.label?.replace(/s$/, '')}
            </button>
          </div>
        ) : (
          <div className="wb-elements-list">
            {filteredElements.map(el => (
              <div
                key={el.id}
                className={`wb-element-card ${expandedId === el.id ? 'wb-element-expanded' : ''}`}
              >
                <div
                  className="wb-element-header"
                  onClick={() => setExpandedId(expandedId === el.id ? null : el.id)}
                >
                  <div>
                    <h4 style={{ margin: 0, color: '#e0e0e0' }}>{el.name}</h4>
                    {el.description && (
                      <p style={{ fontSize: '0.85rem', margin: '0.25rem 0 0 0', color: '#a0a0b8' }}>
                        {expandedId === el.id ? el.description : el.description.slice(0, 100) + (el.description.length > 100 ? '...' : '')}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      className="btn btn-secondary"
                      onClick={(e) => { e.stopPropagation(); openEditForm(el); }}
                      style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem' }}
                    >
                      ✏️
                    </button>
                    <button
                      className="btn btn-secondary"
                      onClick={(e) => { e.stopPropagation(); handleDelete(el.id); }}
                      style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', color: '#ff4444' }}
                    >
                      ✕
                    </button>
                  </div>
                </div>

                {expandedId === el.id && (
                  <div className="wb-element-details">
                    {/* Properties */}
                    {el.properties && Object.keys(el.properties).length > 0 && (
                      <div className="wb-detail-section">
                        <strong>Properties</strong>
                        <div className="wb-properties-display">
                          {Object.entries(el.properties).map(([key, value]) => (
                            value && (
                              <div key={key} className="wb-property-item">
                                <span className="wb-property-label">{key.replace(/_/g, ' ')}</span>
                                <span className="wb-property-value">{value}</span>
                              </div>
                            )
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Connections */}
                    {el.connections && el.connections.length > 0 && (
                      <div className="wb-detail-section">
                        <strong>Connections</strong>
                        <div className="flex gap-2" style={{ flexWrap: 'wrap', marginTop: '0.3rem' }}>
                          {el.connections.map((conn, i) => (
                            <span key={i} className="wb-tag">{conn}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Tags */}
                    {el.tags && el.tags.length > 0 && (
                      <div className="wb-detail-section">
                        <strong>Tags</strong>
                        <div className="flex gap-2" style={{ flexWrap: 'wrap', marginTop: '0.3rem' }}>
                          {el.tags.map((tag, i) => (
                            <span key={i} className="wb-tag" style={{ background: '#2a1a4a', color: '#a855f7' }}>#{tag}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Notes */}
                    {el.notes && (
                      <div className="wb-detail-section">
                        <strong>Notes</strong>
                        <p style={{ fontSize: '0.85rem', color: '#a0a0b8', marginTop: '0.25rem' }}>{el.notes}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default WorldBuilding;
