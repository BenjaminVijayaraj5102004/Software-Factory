import React, { useState, useEffect } from 'react';
import { Sun, Moon, BarChart2, CheckCircle2, Wifi, WifiOff } from 'lucide-react';
import { ProductivityStats } from '../types/todo';

interface HeaderProps {
  stats: ProductivityStats;
  isLive: boolean;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  onOpenAnalytics: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  stats,
  isLive,
  theme,
  onToggleTheme,
  onOpenAnalytics,
}) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(
        now.toLocaleDateString(undefined, {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
        }) +
          ' · ' +
          now.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="neo-box" style={{ padding: '1rem 1.5rem', marginBottom: '1.75rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Brand & Date */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              border: '2.5px solid var(--border-color)',
              borderRadius: '8px',
              background: 'var(--glass-yellow)',
              boxShadow: 'var(--shadow-sm)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 900,
              fontSize: '1.3rem',
              color: '#0f172a',
            }}
          >
            ✓
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h1 style={{ fontSize: '1.45rem', fontWeight: 900, letterSpacing: '-0.03em' }}>
                NEO<span style={{ color: 'var(--glass-yellow-border)' }}>//</span>TODO
              </h1>
              <span className="neo-badge glass-tag-learning" style={{ fontSize: '0.65rem' }}>
                Neo-Brutalism & Glass
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>
              {timeStr}
            </p>
          </div>
        </div>

        {/* Progress & Quick Actions */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          
          {/* Connection Status Badge */}
          <div
            className={`neo-badge ${isLive ? 'glass-tag-devops' : 'glass-tag-learning'}`}
            title={isLive ? 'Connected to FastAPI Backend at /api/v1' : 'Operating in offline cache mode with localStorage'}
            style={{ padding: '0.4rem 0.75rem', cursor: 'default' }}
          >
            {isLive ? <Wifi size={14} /> : <WifiOff size={14} />}
            <span>{isLive ? 'API LIVE' : 'OFFLINE SYNC'}</span>
          </div>

          {/* Quick Stats Pill */}
          <div
            className="neo-box"
            style={{
              padding: '0.4rem 0.85rem',
              borderRadius: '9999px',
              background: 'var(--glass-card-elevated)',
              boxShadow: 'var(--shadow-sm)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.6rem',
              fontSize: '0.85rem',
              fontWeight: 700,
            }}
          >
            <CheckCircle2 size={16} color="var(--glass-mint-border)" />
            <span>
              {stats.completed} / {stats.total} Completed ({stats.completionRate}%)
            </span>
            <div
              style={{
                width: '60px',
                height: '8px',
                border: '1.5px solid var(--border-color)',
                borderRadius: '4px',
                background: 'rgba(0,0,0,0.1)',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  width: `${stats.completionRate}%`,
                  height: '100%',
                  background: 'var(--glass-mint-border)',
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
          </div>

          {/* Analytics Trigger */}
          <button
            onClick={onOpenAnalytics}
            className="neo-btn neo-btn-lavender"
            title="Open Productivity & Analytics Overview"
            style={{ padding: '0.5rem 0.9rem' }}
          >
            <BarChart2 size={16} />
            <span>Analytics</span>
          </button>

          {/* Theme Switcher */}
          <button
            onClick={onToggleTheme}
            className="neo-btn"
            title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
            style={{ padding: '0.5rem 0.75rem' }}
          >
            {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
          </button>

        </div>

      </div>
    </header>
  );
};
