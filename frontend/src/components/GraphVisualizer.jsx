import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer';
import api from '../services/api';

const TYPE_COLORS = {
  novel: 0xffffff,
  character: 0x6c63ff,
  chapter: 0x38bdf8,
  location: 0x10b981,
  plot: 0xf59e0b,
  item: 0xef4444,
  concept: 0x8b5cf6,
  event: 0xec4899,
};

const TYPE_LABELS = {
  novel: '📖 Novel',
  character: '👤 Character',
  chapter: '📑 Chapter',
  location: '📍 Location',
  plot: '📌 Plot',
  item: '🔮 Item',
  concept: '💡 Concept',
  event: '⚡ Event',
};

function GraphVisualizer({ novelId }) {
  const containerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);

  useEffect(() => {
    if (novelId) {
      fetchGraphData();
    }
  }, [novelId]);

  useEffect(() => {
    if (graphData && containerRef.current) {
      return initThreeJS();
    }
  }, [graphData]);

  const fetchGraphData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/memory/graph/${novelId}`);
      setGraphData(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load memory graph');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const initThreeJS = () => {
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight || 600;
    
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0f);

    // Camera
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(15, 10, 15);
    camera.lookAt(0, 0, 0);

    // WebGL Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // CSS2D Renderer for text labels
    const labelRenderer = new CSS2DRenderer();
    labelRenderer.setSize(width, height);
    labelRenderer.domElement.style.position = 'absolute';
    labelRenderer.domElement.style.top = '0';
    labelRenderer.domElement.style.left = '0';
    labelRenderer.domElement.style.pointerEvents = 'none';
    container.appendChild(labelRenderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.3;
    controls.maxDistance = 40;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404060);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(10, 20, 10);
    scene.add(directionalLight);
    const backLight = new THREE.DirectionalLight(0x6c63ff, 0.5);
    backLight.position.set(-10, -5, -10);
    scene.add(backLight);

    // Create nodes and edges
    const { nodes = [], edges = [] } = graphData;
    const nodeMap = {};
    const meshToNode = new Map();

    // Create nodes
    nodes.forEach((node, index) => {
      // Position nodes in a sphere distribution
      const phi = Math.acos(2 * (index / Math.max(nodes.length, 1)) - 1);
      const theta = Math.PI * (1 + Math.sqrt(5)) * index;
      const radius = 5 + Math.random() * 3;

      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);

      // Node sphere - size based on type
      const isNovel = node.type === 'novel';
      const nodeSize = isNovel ? 0.6 : 0.35;
      const nodeGeometry = new THREE.SphereGeometry(nodeSize, 16, 16);
      const nodeMaterial = new THREE.MeshStandardMaterial({
        color: TYPE_COLORS[node.type] || 0x6c63ff,
        emissive: TYPE_COLORS[node.type] || 0x6c63ff,
        emissiveIntensity: 0.2,
        metalness: 0.5,
        roughness: 0.2,
      });

      const mesh = new THREE.Mesh(nodeGeometry, nodeMaterial);
      mesh.position.set(x, y, z);
      mesh.userData = { id: node.id, label: node.label, type: node.type, data: node.data };
      scene.add(mesh);
      meshToNode.set(mesh, node);

      // ── CSS2D Label ──────────────────────────────────────────
      const labelDiv = document.createElement('div');
      labelDiv.className = 'graph-node-label';
      labelDiv.style.cssText = `
        color: #e0e0e0;
        font-size: 11px;
        font-family: 'Inter', -apple-system, sans-serif;
        background: rgba(10, 10, 15, 0.85);
        padding: 3px 8px;
        border-radius: 4px;
        border: 1px solid #${(TYPE_COLORS[node.type] || 0x6c63ff).toString(16).padStart(6, '0')}44;
        white-space: nowrap;
        pointer-events: none;
        max-width: 160px;
        overflow: hidden;
        text-overflow: ellipsis;
      `;

      // Type badge
      const typeColor = '#' + (TYPE_COLORS[node.type] || 0x6c63ff).toString(16).padStart(6, '0');
      const typeBadge = `<span style="color:${typeColor};font-size:9px;font-weight:600;text-transform:uppercase;margin-right:4px;">${node.type}</span>`;

      // Node label
      const displayLabel = (node.label || '').length > 20 ? node.label.slice(0, 18) + '…' : (node.label || '');
      labelDiv.innerHTML = `${typeBadge}${displayLabel}`;

      // Extra data for key types
      if (node.data) {
        const extraInfo = [];
        if (node.data.role) extraInfo.push(node.data.role);
        if (node.data.word_count) extraInfo.push(`${node.data.word_count}w`);
        if (node.data.event_type) extraInfo.push(node.data.event_type);
        if (node.data.genre) extraInfo.push(node.data.genre);

        if (extraInfo.length > 0) {
          labelDiv.innerHTML += `<br/><span style="color:#a0a0b8;font-size:9px;">${extraInfo.join(' · ')}</span>`;
        }
      }

      const label = new CSS2DObject(labelDiv);
      label.position.set(0, nodeSize + 0.3, 0);
      mesh.add(label);

      nodeMap[node.id] = { mesh, position: { x, y, z } };
    });

    // Create edges
    edges.forEach((edge) => {
      const source = nodeMap[edge.source];
      const target = nodeMap[edge.target];
      if (source && target) {
        const points = [
          new THREE.Vector3(source.position.x, source.position.y, source.position.z),
          new THREE.Vector3(target.position.x, target.position.y, target.position.z),
        ];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        
        // Edge color based on relationship type
        const edgeColor = edge.type === 'has_character' ? 0x6c63ff
          : edge.type === 'has_chapter' ? 0x38bdf8
          : edge.type === 'involves' ? 0xf59e0b
          : edge.type === 'occurs_in' ? 0x10b981
          : 0x2a2a4a;
        
        const edgeMaterial = new THREE.LineBasicMaterial({
          color: edgeColor,
          transparent: true,
          opacity: 0.4,
        });

        const line = new THREE.Line(geometry, edgeMaterial);
        scene.add(line);

        // Edge label (only for relationship edges, not structural ones)
        if (edge.type && !['has_character', 'has_chapter'].includes(edge.type)) {
          const midX = (source.position.x + target.position.x) / 2;
          const midY = (source.position.y + target.position.y) / 2;
          const midZ = (source.position.z + target.position.z) / 2;

          const edgeLabelDiv = document.createElement('div');
          edgeLabelDiv.style.cssText = `
            color: #6c63ff;
            font-size: 9px;
            font-family: 'Inter', sans-serif;
            background: rgba(10, 10, 15, 0.7);
            padding: 1px 5px;
            border-radius: 3px;
            pointer-events: none;
          `;
          edgeLabelDiv.textContent = edge.type.replace(/_/g, ' ');

          const edgeLabel = new CSS2DObject(edgeLabelDiv);
          edgeLabel.position.set(midX, midY, midZ);
          scene.add(edgeLabel);
        }
      }
    });

    // Raycaster for hover effects
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let hoveredMesh = null;

    const onMouseMove = (event) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const meshes = Object.values(nodeMap).map(n => n.mesh);
      const intersects = raycaster.intersectObjects(meshes);

      // Reset previous hover
      if (hoveredMesh) {
        hoveredMesh.material.emissiveIntensity = 0.2;
        hoveredMesh.scale.set(1, 1, 1);
      }

      if (intersects.length > 0) {
        hoveredMesh = intersects[0].object;
        hoveredMesh.material.emissiveIntensity = 0.6;
        hoveredMesh.scale.set(1.3, 1.3, 1.3);
        renderer.domElement.style.cursor = 'pointer';

        const nodeData = hoveredMesh.userData;
        setHoveredNode(nodeData);
      } else {
        hoveredMesh = null;
        renderer.domElement.style.cursor = 'grab';
        setHoveredNode(null);
      }
    };

    renderer.domElement.addEventListener('mousemove', onMouseMove);

    // Animation loop
    let frameId;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
      labelRenderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight || 600;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
      labelRenderer.setSize(newWidth, newHeight);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener('resize', handleResize);
      renderer.domElement.removeEventListener('mousemove', onMouseMove);
      if (renderer.domElement.parentNode === container) {
        container.removeChild(renderer.domElement);
      }
      if (labelRenderer.domElement.parentNode === container) {
        container.removeChild(labelRenderer.domElement);
      }
      renderer.dispose();
    };
  };

  if (loading) {
    return (
      <div className="card" style={{ height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>🕸️ Loading memory graph...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" style={{ height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: '#ff6666' }}>{error}</p>
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: '0', overflow: 'hidden', position: 'relative' }}>
      {/* Info overlay */}
      <div className="graph-info-overlay">
        <span>🕸️ {graphData?.nodes?.length || 0} nodes • {graphData?.edges?.length || 0} connections</span>
      </div>

      {/* Legend */}
      <div className="graph-legend">
        {Object.entries(TYPE_LABELS).map(([type, label]) => (
          <div key={type} className="graph-legend-item">
            <span
              className="graph-legend-dot"
              style={{ background: '#' + (TYPE_COLORS[type] || 0x6c63ff).toString(16).padStart(6, '0') }}
            />
            <span>{label}</span>
          </div>
        ))}
      </div>

      {/* Hover tooltip */}
      {hoveredNode && (
        <div className="graph-tooltip">
          <strong>{hoveredNode.label}</strong>
          <span style={{ color: '#6c63ff', fontSize: '0.75rem', textTransform: 'uppercase' }}>
            {hoveredNode.type}
          </span>
          {hoveredNode.data?.role && <span>Role: {hoveredNode.data.role}</span>}
          {hoveredNode.data?.description && (
            <span style={{ fontSize: '0.8rem', color: '#a0a0b8' }}>
              {hoveredNode.data.description?.slice(0, 100)}
            </span>
          )}
        </div>
      )}

      {/* 3D Canvas */}
      <div 
        ref={containerRef} 
        style={{ 
          height: '600px', 
          width: '100%',
          background: '#0a0a0f',
          cursor: 'grab',
          position: 'relative'
        }} 
      />

      <div className="graph-controls-hint">
        Drag to rotate • Scroll to zoom • Hover nodes for details
      </div>
    </div>
  );
}

export default GraphVisualizer;
