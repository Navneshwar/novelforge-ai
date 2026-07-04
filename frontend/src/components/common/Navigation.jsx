import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  BookOpen,
  Compass,
  Users,
  Globe,
  Clock,
  Brain,
  BarChart3,
  Settings,
  ChevronDown,
  Menu,
  X
} from 'lucide-react';
import '../styles/Navigation.css';

const Navigation = () => {
  const location = useLocation();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const navItems = [
    { label: 'Discover', icon: Compass, href: '/' },
    { label: 'Workspace', icon: BookOpen, href: '/workspace' },
    { label: 'Characters', icon: Users, href: '/characters' },
    { label: 'World', icon: Globe, href: '/world' },
    { label: 'Timeline', icon: Clock, href: '/timeline' },
    { label: 'Memory', icon: Brain, href: '/memory' },
    { label: 'Analytics', icon: BarChart3, href: '/analytics' },
  ];

  const isActive = (href) => location.pathname === href;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Logo */}
        <Link to="/" className="navbar-logo">
          <BookOpen size={24} />
          <span>NovelForge</span>
        </Link>

        {/* Mobile Menu Button */}
        <button
          className="navbar-mobile-toggle"
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          aria-label="Toggle menu"
        >
          {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>

        {/* Navigation Links */}
        <div className={`navbar-menu ${isMobileOpen ? 'active' : ''}`}>
          <div className="navbar-nav">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className={`nav-item ${active ? 'active' : ''}`}
                  onClick={() => setIsMobileOpen(false)}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                  {active && <div className="nav-item-indicator" />}
                </Link>
              );
            })}
          </div>

          {/* Settings */}
          <Link
            to="/settings"
            className={`nav-item nav-settings ${isActive('/settings') ? 'active' : ''}`}
            onClick={() => setIsMobileOpen(false)}
          >
            <Settings size={20} />
            <span>Settings</span>
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;