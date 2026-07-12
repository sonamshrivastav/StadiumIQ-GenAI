import { useState, useEffect } from 'react';

export default function Header({ stadium, stadiumId }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="header" role="banner">
      {/* Skip to main content link for keyboard/screen reader users */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <div className="header__left">
        <div className="header__logo">
          <span className="header__logo-icon" aria-hidden="true">⚽</span>
          <div className="header__logo-text">
            Stadium<span>IQ</span>
          </div>
        </div>
        {stadium && (
          <div className="header__stadium-badge">
            <span className="live-dot" aria-hidden="true"></span>
            <span aria-hidden="true">🏟️</span> {stadium.name} — {stadium.city}
          </div>
        )}
      </div>
      <div className="header__right">
        <div className="header__time" aria-live="off" aria-label={`Current time: ${time.toLocaleTimeString()}`}>
          {time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
        </div>
      </div>
    </header>
  );
}
