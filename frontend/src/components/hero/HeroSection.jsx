import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, Upload } from 'lucide-react';
import '../styles/HeroSection.css';

const HeroSection = () => {
  return (
    <section className="hero">
      <div className="hero-container">
        {/* Left Content */}
        <div className="hero-content">
          <div className="hero-divider" />
          
          <h1 className="hero-title">
            <span className="hero-title-line">Write Stories</span>
            <span className="hero-title-line">that never forget.</span>
          </h1>

          <p className="hero-subtitle">
            AI-powered writing with persistent memory,
            <br />
            characters, world building
            <br />
            and intelligent planning.
          </p>

          <div className="hero-divider" />

          {/* CTA Buttons */}
          <div className="hero-cta">
            <Link to="/workspace/new" className="btn btn-primary">
              <BookOpen size={20} />
              Create Novel
              <ArrowRight size={18} />
            </Link>
            <Link to="/workspace/import" className="btn btn-secondary">
              <Upload size={20} />
              Import Existing
            </Link>
          </div>
        </div>

        {/* Right Illustration Area */}
        <div className="hero-illustration">
          <div className="illustration-wrapper">
            {/* Floating Books */}
            <div className="floating-book book-1">
              <div className="book-cover" />
            </div>
            <div className="floating-book book-2">
              <div className="book-cover" />
            </div>
            <div className="floating-book book-3">
              <div className="book-cover" />
            </div>

            {/* Abstract Elements */}
            <div className="abstract-wave wave-1" />
            <div className="abstract-wave wave-2" />
            <div className="abstract-blob blob-1" />
            <div className="abstract-blob blob-2" />

            {/* Ink Drops */}
            <div className="ink-drop ink-1" />
            <div className="ink-drop ink-2" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;