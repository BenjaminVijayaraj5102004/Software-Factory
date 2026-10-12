import React, { useState } from 'react';
import { X, Save, AlertCircle, Tag, Calendar } from 'lucide-react';
import { TodoItem, Priority, Category } from '../types/todo';

interface EditTaskModalProps {
  todo: TodoItem;
  categories: Category[];
  onSave: (id: string, updates: Partial<TodoItem>) => void;
  onClose: () => void;
}

export const EditTaskModal: React.FC<EditTaskModalProps> = ({
  todo,
  categories,
  onSave,
  onClose,
}) => {
  const [title, setTitle] = useState(todo.title);
  const [description, setDescription] = useState(todo.description || '');
  const [priority, setPriority] = useState<Priority>(todo.priority);
  const [category, setCategory] = useState(todo.category);
  const [dueDate, setDueDate] = useState(
    todo.dueDate ? new Date(todo.dueDate).toISOString().split('T')[0] : ''
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    onSave(todo.id, {
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      category,
      dueDate: dueDate ? new Date(dueDate).toISOString() : undefined,
    });
    onClose();
  };

  const priorityOptions: { value: Priority; label: string; colorClass: string }[] = [
    { value: 'urgent', label: 'Urgent', colorClass: 'glass-tag-urgent' },
    { value: 'high', label: 'High', colorClass: 'glass-tag-learning' },
    { value: 'medium', label: 'Medium', colorClass: 'glass-tag-work' },
    { value: 'low', label: 'Low', colorClass: 'glass-tag-devops' },
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="neo-box"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: '520px',
          padding: '1.75rem',
          background: 'var(--glass-card-elevated)',
          boxShadow: 'var(--shadow-xl)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 900 }}>Edit Task</h2>
          <button
            onClick={onClose}
            className="neo-btn"
            style={{ padding: '0.35rem 0.6rem' }}
            title="Close modal"
          >
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 800, marginBottom: '0.35rem' }}>
              Title
            </label>
            <input
              type="text"
              className="neo-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 800, marginBottom: '0.35rem' }}>
              Description / Notes
            </label>
            <textarea
              className="neo-input"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add extra context or instructions..."
              style={{ resize: 'vertical' }}
            />
          </div>

          {/* Priority selection */}
          <div>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.85rem', fontWeight: 800, marginBottom: '0.35rem' }}>
              <AlertCircle size={14} /> Priority
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {priorityOptions.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setPriority(opt.value)}
                  className={`neo-badge ${opt.colorClass}`}
                  style={{
                    cursor: 'pointer',
                    borderWidth: priority === opt.value ? '2.5px' : '1.5px',
                    transform: priority === opt.value ? 'scale(1.05)' : 'none',
                    boxShadow: priority === opt.value ? 'var(--shadow-sm)' : 'none',
                  }}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Category & Due Date Row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.85rem', fontWeight: 800, marginBottom: '0.35rem' }}>
                <Tag size={14} /> Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="neo-input"
                style={{ fontWeight: 700 }}
              >
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.85rem', fontWeight: 800, marginBottom: '0.35rem' }}>
                <Calendar size={14} /> Due Date
              </label>
              <input
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="neo-input"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
            <button type="button" onClick={onClose} className="neo-btn">
              Cancel
            </button>
            <button type="submit" className="neo-btn neo-btn-primary">
              <Save size={16} />
              <span>Save Changes</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
