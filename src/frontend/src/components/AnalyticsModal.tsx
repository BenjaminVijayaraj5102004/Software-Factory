import React from 'react';
import { X, Award, Download, FileSpreadsheet, CheckCircle, Clock, AlertTriangle, Flame } from 'lucide-react';
import { ProductivityStats, TodoItem } from '../types/todo';

interface AnalyticsModalProps {
  stats: ProductivityStats;
  todos: TodoItem[];
  onExportJson: () => void;
  onExportCsv: () => void;
  onClose: () => void;
}

export const AnalyticsModal: React.FC<AnalyticsModalProps> = ({
  stats,
  todos,
  onExportJson,
  onExportCsv,
  onClose,
}) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="neo-box"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: '640px',
          padding: '1.75rem',
          background: 'var(--glass-card-elevated)',
          boxShadow: 'var(--shadow-xl)',
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                border: '2px solid var(--border-color)',
                background: 'var(--glass-lavender)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#4c1d95',
              }}
            >
              <Award size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 900 }}>Productivity Analytics</h2>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Real-time metrics, streaks & backup exports
              </p>
            </div>
          </div>
          <button onClick={onClose} className="neo-btn" style={{ padding: '0.35rem 0.6rem' }}>
            <X size={16} />
          </button>
        </div>

        {/* Top Metric Cards Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.85rem', marginBottom: '1.5rem' }}>
          
          <div className="neo-box" style={{ padding: '0.85rem', background: 'var(--glass-mint)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#064e3b', marginBottom: '0.25rem' }}>
              <CheckCircle size={15} />
              <span style={{ fontSize: '0.75rem', fontWeight: 800 }}>COMPLETED</span>
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 900, color: '#064e3b' }}>
              {stats.completed} <span style={{ fontSize: '0.9rem', fontWeight: 700 }}>/ {stats.total}</span>
            </div>
          </div>

          <div className="neo-box" style={{ padding: '0.85rem', background: 'var(--glass-yellow)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#713f12', marginBottom: '0.25rem' }}>
              <Clock size={15} />
              <span style={{ fontSize: '0.75rem', fontWeight: 800 }}>IN PROGRESS</span>
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 900, color: '#713f12' }}>
              {stats.pending}
            </div>
          </div>

          <div className="neo-box" style={{ padding: '0.85rem', background: 'var(--glass-coral)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#881337', marginBottom: '0.25rem' }}>
              <AlertTriangle size={15} />
              <span style={{ fontSize: '0.75rem', fontWeight: 800 }}>OVERDUE</span>
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 900, color: '#881337' }}>
              {stats.overdue}
            </div>
          </div>

          <div className="neo-box" style={{ padding: '0.85rem', background: 'var(--glass-peach)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#7c2d12', marginBottom: '0.25rem' }}>
              <Flame size={15} />
              <span style={{ fontSize: '0.75rem', fontWeight: 800 }}>STREAK</span>
            </div>
            <div style={{ fontSize: '1.75rem', fontWeight: 900, color: '#7c2d12' }}>
              {stats.streakDays} <span style={{ fontSize: '0.9rem', fontWeight: 700 }}>days</span>
            </div>
          </div>

        </div>

        {/* Priority Breakdown */}
        <div className="neo-box" style={{ padding: '1.15rem', marginBottom: '1.25rem', background: 'var(--glass-card)' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 900, marginBottom: '0.85rem' }}>
            Task Distribution by Priority
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {(['urgent', 'high', 'medium', 'low'] as const).map((p) => {
              const count = stats.byPriority[p] || 0;
              const pct = stats.total > 0 ? Math.round((count / stats.total) * 100) : 0;
              return (
                <div key={p}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.2rem' }}>
                    <span style={{ textTransform: 'capitalize' }}>{p}</span>
                    <span>{count} tasks ({pct}%)</span>
                  </div>
                  <div
                    style={{
                      height: '8px',
                      borderRadius: '4px',
                      border: '1px solid var(--border-color)',
                      background: 'rgba(0,0,0,0.08)',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        width: `${pct}%`,
                        height: '100%',
                        background:
                          p === 'urgent'
                            ? 'var(--glass-coral-border)'
                            : p === 'high'
                            ? 'var(--glass-peach-border)'
                            : p === 'medium'
                            ? 'var(--glass-cyan-border)'
                            : 'var(--glass-mint-border)',
                        transition: 'width 0.3s ease',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Export & Data Backup Section */}
        <div className="neo-box" style={{ padding: '1.15rem', background: 'var(--glass-card)' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 900, marginBottom: '0.4rem' }}>
            Data Backup & Portability
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
            Export your tasks to formatted JSON backup or a CSV spreadsheet anytime.
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button
              onClick={onExportJson}
              className="neo-btn neo-btn-mint"
              style={{ flex: 1, minWidth: '150px' }}
            >
              <Download size={16} />
              <span>Download JSON</span>
            </button>
            <button
              onClick={onExportCsv}
              className="neo-btn neo-btn-lavender"
              style={{ flex: 1, minWidth: '150px' }}
            >
              <FileSpreadsheet size={16} />
              <span>Download CSV</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
