import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import NovelPage from './pages/NovelPage';
import './styles/theme.css';
import './styles/components.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              📖 NovelForge
            </Link>
            <div className="nav-links">
              <Link to="/" className="nav-link">Dashboard</Link>
              <Link to="/novel/new" className="nav-link">New Novel</Link>
            </div>
          </div>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/novel/:id" element={<NovelPage />} />
            <Route path="/novel/new" element={<NovelPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;