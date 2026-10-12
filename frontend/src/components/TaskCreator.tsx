import React, { useState } from 'react';
import { Plus, Calendar, Tag, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Priority, Category } from '../types/todo';

interface TaskCreatorProps {
  categories: Category[];
  onAddTask: (data: {
    title: string;
    description?: string;
    priority: Priority;
    category: string;
    dueDate?: string;
  }) => void;
}

export const TaskCreator: React.FC<TaskCreatorProps> = ({ categories, onAddTask }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [category, setCategory] = useState<string>('work');
  const [dueDate, setDueDate] = useState<string>('');
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    onAddTask({
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      category,
      dueDate: dueDate ? new Date(dueDate).toISOString() : undefined,
    });

    setTitle('');
    setDescription('');
    setDueDate('');
    setIsExpanded(false);
  };

  const priorityOptions: { value: Priority; label: string; colorClass: string }[] = [
    { value: 'urgent', label: 'Urgent', colorClass: 'glass-tag-urgent' },
    { value: 'high', label: 'High', colorClass: 'glass-tag-learning' },
    { value: 'medium', label: 'Medium', colorClass: 'glass-tag-work' },
    { value: 'low', label: 'Low', colorClass: 'glass-tag-devops' },
  ];

  return (
    <section className="neo-box" style={{ padding: '1.25rem', marginBottom: '1.75rem' }}>
      <form onSubmit={handleSubmit}>
        
        {/* Main Input Row */}
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'stretch' }}>
          <input
            type="text"
            className="neo-input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="What needs to be accomplished today? (Press Enter to add)"
            style={{ fontSize: '1.05rem', fontWeight: 600, flex: 1 }}
          />

          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="neo-btn"
            title="Toggle extra options"
            style={{ padding: '0 0.85rem' }}
          >
            {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>

          <button
            type="submit"
            disabled={!title.trim()}
            className="neo-btn neo-btn-primary"
            style={{ whiteSpace: 'nowrap', padding: '0 1.25rem' }}
          >
            <Plus size={18} />
            <span>Add Task</span>
          </button>
        </div>

        {/* Collapsible Details Row */}
        {isExpanded && (
          <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <textarea
              className="neo-input"
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add optional notes, requirements, or link to pull request..."
              style={{ resize: 'vertical' }}
            />

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center', justifyContent: 'space-between' }}>
              
              {/* Priority Chips */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <AlertCircle size={14} /> Priority:
                </span>
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

              {/* Category Dropdown/Chips */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Tag size={14} /> Category:
                </span>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="neo-input"
                  style={{ width: 'auto', padding: '0.35rem 0.75rem', fontSize: '0.85rem', fontWeight: 700 }}
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Due Date Input */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <Calendar size={14} /> Due Date:
                </span>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="neo-input"
                  style={{ width: 'auto', padding: '0.35rem 0.6rem', fontSize: '0.85rem' }}
                />
              </div>

            </div>
          </div>
        )}

      </form>
    </section>
  );
};
