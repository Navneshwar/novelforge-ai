import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import api from '../services/api';

function GraphVisualizer({ novelId }) {
  const containerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [graphData, setGraphData] = useState(null);

  useEffect(() => {
    if (novelId) {
      fetchGraphData();
    }
  }, [novelId]);

  useEffect(() => {
    if (graphData && containerRef.current) {
      initThreeJS();
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
    const height = container.clientHeight || 500;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0f);

    // Camera
    const camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
    camera.position.set(15, 10, 15);
    camera.lookAt(0, 0, 0);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.5;
    controls.maxDistance = 30;

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

    // Create nodes
    const nodeGeometry = new THREE.SphereGeometry(0.4, 16, 16);
    const nodeMaterial = new THREE.MeshStandardMaterial({
      color: 0x6c63ff,
      emissive: 0x3a2a7a,
      emissiveIntensity: 0.3,
      metalness: 0.5,
      roughness: 0.2,
    });

    nodes.forEach((node, index) => {
      // Position nodes in a sphere distribution
      const phi = Math.acos(2 * (index / nodes.length) - 1);
      const theta = Math.PI * (1 + Math.sqrt(5)) * index;
      const radius = 5 + Math.random() * 3;

      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.sin(phi) * Math.sin(theta);
      const z = radius * Math.cos(phi);

      const mesh = new THREE.Mesh(nodeGeometry, nodeMaterial.clone());
      mesh.position.set(x, y, z);
      
      // Color based on type
      const typeColors = {
        character: 0x6c63ff,
        location: 0x10b981,
        plot: 0xf59e0b,
        item: 0xef4444,
        concept: 0x8b5cf6,
        event: 0xec4899,
      };
      mesh.material.color.setHex(typeColors[node.type] || 0x6c63ff);
      
      mesh.userData = { id: node.id, label: node.label };
      scene.add(mesh);
      nodeMap[node.id] = { mesh, position: { x, y, z } };
    });

    // Create edges
    const edgeMaterial = new THREE.LineBasicMaterial({
      color: 0x2a2a4a,
      transparent: true,
      opacity: 0.5,
    });

    edges.forEach((edge) => {
      const source = nodeMap[edge.source];
      const target = nodeMap[edge.target];
      if (source && target) {
        const points = [
          new THREE.Vector3(source.position.x, source.position.y, source.position.z),
          new THREE.Vector3(target.position.x, target.position.y, target.position.z),
        ];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const line = new THREE.Line(geometry, edgeMaterial);
        scene.add(line);
      }
    });

    // Animation loop
    let frameId;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Handle resize
    const handleResize = () => {
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight || 500;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener('resize', handleResize);
      container.removeChild(renderer.domElement);
      renderer.dispose();
    };
  };

  if (loading) {
    return (
      <div className="card" style={{ height: '500px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>🕸️ Loading memory graph...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" style={{ height: '500px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: '#ff6666' }}>{error}</p>
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: '0', overflow: 'hidden', position: 'relative' }}>
      <div style={{ 
        position: 'absolute', 
        top: '10px', 
        left: '10px', 
        zIndex: 10,
        background: 'rgba(10,10,15,0.8)',
        padding: '0.5rem 1rem',
        borderRadius: '8px',
        fontSize: '0.85rem'
      }}>
        <span>🕸️ {graphData?.nodes?.length || 0} nodes • {graphData?.edges?.length || 0} connections</span>
      </div>
      <div 
        ref={containerRef} 
        style={{ 
          height: '500px', 
          width: '100%',
          background: '#0a0a0f',
          cursor: 'grab'
        }} 
      />
      <div style={{ 
        position: 'absolute', 
        bottom: '10px', 
        right: '10px', 
        zIndex: 10,
        background: 'rgba(10,10,15,0.8)',
        padding: '0.3rem 0.8rem',
        borderRadius: '4px',
        fontSize: '0.7rem',
        color: '#6c63ff'
      }}>
        Drag to rotate • Scroll to zoom
      </div>
    </div>
  );
}

export default GraphVisualizer;