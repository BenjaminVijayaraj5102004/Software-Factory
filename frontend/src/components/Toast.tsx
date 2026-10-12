import React from 'react';
import { Check, Info, AlertTriangle, X } from 'lucide-react';

export interface ToastMessage {
  id: string;
  type: 'success' | 'info' | 'warning';
  text: string;
}

interface ToastProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const Toast: React.FC<ToastProps> = ({ toasts, onDismiss }) => {
  if (toasts.length === 0) return null;

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '1.5rem',
        right: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.65rem',
        zIndex: 200,
        maxWidth: '360px',
      }}
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          className="neo-box"
          style={{
            padding: '0.75rem 1rem',
            background:
              t.type === 'success'
                ? 'var(--glass-mint)'
                : t.type === 'warning'
                ? 'var(--glass-coral)'
                : 'var(--glass-yellow)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '0.75rem',
            fontSize: '0.88rem',
            fontWeight: 700,
            color: '#0f172a',
            boxShadow: 'var(--shadow-md)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {t.type === 'success' && <Check size={16} color="#064e3b" />}
            {t.type === 'warning' && <AlertTriangle size={16} color="#881337" />}
            {t.type === 'info' && <Info size={16} color="#713f12" />}
            <span>{t.text}</span>
          </div>
          <button
            onClick={() => onDismiss(t.id)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: '#0f172a',
              display: 'flex',
            }}
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
};
