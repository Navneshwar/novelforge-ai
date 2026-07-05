import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import NovelPage from './pages/NovelPage';
import Login from './pages/Login';
import Register from './pages/Register';
import ProtectedRoute from './components/auth/ProtectedRoute';
import { AuthProvider, useAuth } from './context/AuthContext';
import './styles/theme.css';
import './styles/components.css';
import './styles/auth.css';
import './styles/novel-page.css';

function TopNav() {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initial = (user?.display_name || user?.email || '?').trim().charAt(0).toUpperCase();

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          📖 NovelForge
        </Link>
        <div className="nav-links">
          {isAuthenticated && (
            <>
              <Link to="/" className="nav-link">Dashboard</Link>
              <Link to="/novel/new" className="nav-link">New Novel</Link>
            </>
          )}

          {isAuthenticated ? (
            <div className="nav-user-menu">
              <div className="nav-user-avatar" title={user?.email}>{initial}</div>
              <button className="nav-logout-btn" onClick={handleLogout}>
                <LogOut size={16} />
                Log out
              </button>
            </div>
          ) : (
            <>
              <Link to="/login" className="nav-link">Sign in</Link>
              <Link to="/register" className="btn btn-primary btn-small">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

function AppShell() {
  return (
    <div className="app">
      <TopNav />
      <main className="main-content">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/novel/:id"
            element={
              <ProtectedRoute>
                <NovelPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/novel/new"
            element={
              <ProtectedRoute>
                <NovelPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppShell />
      </AuthProvider>
    </Router>
  );
}

export default App;
