import React, { useState } from 'react';
import { Calendar, CheckSquare, Clock, Edit3, Trash2, ChevronDown, ChevronUp, Plus, AlertTriangle } from 'lucide-react';
import { TodoItem, Priority, Subtask } from '../types/todo';

interface TodoCardProps {
  todo: TodoItem;
  onToggleStatus: (id: string, currentStatus: string) => void;
  onDelete: (id: string) => void;
  onEdit: (todo: TodoItem) => void;
  onAddSubtask: (todoId: string, title: string) => void;
  onToggleSubtask: (todoId: string, subtaskId: string, completed: boolean) => void;
  onDeleteSubtask: (todoId: string, subtaskId: string) => void;
}

export const TodoCard: React.FC<TodoCardProps> = ({
  todo,
  onToggleStatus,
  onDelete,
  onEdit,
  onAddSubtask,
  onToggleSubtask,
  onDeleteSubtask,
}) => {
  const [showSubtasks, setShowSubtasks] = useState<boolean>(todo.subtasks.length > 0);
  const [newSubtaskTitle, setNewSubtaskTitle] = useState<string>('');

  const isCompleted = todo.status === 'completed';
  const hasSubtasks = todo.subtasks && todo.subtasks.length > 0;
  const completedSubtasksCount = hasSubtasks ? todo.subtasks.filter((s: Subtask) => s.completed).length : 0;
  const subtaskProgress = hasSubtasks ? Math.round((completedSubtasksCount / todo.subtasks.length) * 100) : 0;

  // Due Date calculation
  let isOverdue = false;
  let formattedDue = '';
  if (todo.dueDate) {
    const due = new Date(todo.dueDate);
    isOverdue = !isCompleted && due < new Date();
    formattedDue = due.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  const priorityColorMap: Record<Priority, string> = {
    urgent: 'glass-tag-urgent',
    high: 'glass-tag-learning',
    medium: 'glass-tag-work',
    low: 'glass-tag-devops',
  };

  const handleSubtaskSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSubtaskTitle.trim()) return;
    onAddSubtask(todo.id, newSubtaskTitle.trim());
    setNewSubtaskTitle('');
  };

  return (
    <article
      className="neo-box"
      style={{
        padding: '1.25rem',
        marginBottom: '1rem',
        opacity: isCompleted ? 0.75 : 1,
        transition: 'all 0.2s ease',
        background: isCompleted ? 'rgba(255, 255, 255, 0.45)' : 'var(--glass-card)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
        
        {/* Tactile Checkbox */}
        <input
          type="checkbox"
          checked={isCompleted}
          onChange={() => onToggleStatus(todo.id, todo.status)}
          className="neo-checkbox"
          title={isCompleted ? 'Mark as active' : 'Mark as completed'}
          style={{ marginTop: '3px' }}
        />

        {/* Content Body */}
        <div style={{ flex: 1, minWidth: 0 }}>
          
          {/* Header Row: Title & Badges */}
          <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem', marginBottom: '0.35rem' }}>
            <h3
              style={{
                fontSize: '1.05rem',
                fontWeight: 800,
                color: 'var(--text-main)',
                textDecoration: isCompleted ? 'line-through' : 'none',
                textDecorationThickness: '2px',
                wordBreak: 'break-word',
              }}
            >
              {todo.title}
            </h3>

            {/* Badges Pill Row */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
              
              {/* Category */}
              <span className={`neo-badge glass-tag-${todo.category}`}>
                {todo.category}
              </span>

              {/* Priority */}
              <span className={`neo-badge ${priorityColorMap[todo.priority]}`}>
                {todo.priority}
              </span>

              {/* Due Date Indicator */}
              {todo.dueDate && (
                <span
                  className="neo-badge"
                  style={{
                    background: isOverdue ? 'var(--glass-coral)' : 'var(--glass-card-elevated)',
                    color: isOverdue ? '#9f1239' : 'var(--text-muted)',
                  }}
                  title={isOverdue ? 'Task is past due date!' : 'Scheduled deadline'}
                >
                  {isOverdue ? <AlertTriangle size={12} /> : <Calendar size={12} />}
                  <span>{formattedDue}</span>
                </span>
              )}

            </div>
          </div>

          {/* Description */}
          {todo.description && (
            <p
              style={{
                fontSize: '0.88rem',
                color: 'var(--text-muted)',
                marginBottom: '0.75rem',
                lineHeight: 1.5,
              }}
            >
              {todo.description}
            </p>
          )}

          {/* Subtasks Progress & Drawer */}
          {hasSubtasks && (
            <div style={{ marginTop: '0.65rem', marginBottom: '0.5rem' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '0.5rem',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  color: 'var(--text-dim)',
                  marginBottom: '0.35rem',
                }}
              >
                <button
                  type="button"
                  onClick={() => setShowSubtasks(!showSubtasks)}
                  style={{
                    background: 'none',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                    cursor: 'pointer',
                    fontWeight: 700,
                    color: 'inherit',
                  }}
                >
                  {showSubtasks ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  <span>
                    Subtasks ({completedSubtasksCount}/{todo.subtasks.length} done · {subtaskProgress}%)
                  </span>
                </button>

                {/* Progress bar */}
                <div
                  style={{
                    width: '100px',
                    height: '6px',
                    border: '1px solid var(--border-color)',
                    borderRadius: '3px',
                    background: 'rgba(0,0,0,0.08)',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${subtaskProgress}%`,
                      height: '100%',
                      background: 'var(--glass-mint-border)',
                      transition: 'width 0.25s ease',
                    }}
                  />
                </div>
              </div>

              {/* Subtasks List */}
              {showSubtasks && (
                <div
                  style={{
                    padding: '0.6rem 0.8rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1.5px solid var(--border-color)',
                    background: 'var(--glass-card-elevated)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.4rem',
                  }}
                >
                  {todo.subtasks.map((st: Subtask) => (
                    <div
                      key={st.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '0.5rem',
                        fontSize: '0.84rem',
                      }}
                    >
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', flex: 1 }}>
                        <input
                          type="checkbox"
                          checked={st.completed}
                          onChange={() => onToggleSubtask(todo.id, st.id, st.completed)}
                          className="neo-checkbox"
                          style={{ width: '16px', height: '16px' }}
                        />
                        <span style={{ textDecoration: st.completed ? 'line-through' : 'none', color: st.completed ? 'var(--text-dim)' : 'inherit' }}>
                          {st.title}
                        </span>
                      </label>
                      <button
                        onClick={() => onDeleteSubtask(todo.id, st.id)}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: 'var(--text-dim)',
                          padding: '2px',
                        }}
                        title="Delete subtask"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  ))}

                  {/* Add Subtask Form */}
                  <form onSubmit={handleSubtaskSubmit} style={{ display: 'flex', gap: '0.4rem', marginTop: '0.4rem' }}>
                    <input
                      type="text"
                      className="neo-input"
                      value={newSubtaskTitle}
                      onChange={(e) => setNewSubtaskTitle(e.target.value)}
                      placeholder="Add subtask..."
                      style={{ padding: '0.3rem 0.6rem', fontSize: '0.8rem' }}
                    />
                    <button
                      type="submit"
                      disabled={!newSubtaskTitle.trim()}
                      className="neo-btn neo-btn-mint"
                      style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }}
                    >
                      <Plus size={14} />
                    </button>
                  </form>
                </div>
              )}
            </div>
          )}

          {/* Action Row */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.65rem' }}>
            {!hasSubtasks && (
              <button
                type="button"
                onClick={() => {
                  setShowSubtasks(true);
                  onAddSubtask(todo.id, 'Initial step');
                }}
                className="neo-btn"
                style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }}
              >
                <Plus size={13} />
                <span>Add Checklist</span>
              </button>
            )}

            <button
              onClick={() => onEdit(todo)}
              className="neo-btn neo-btn-lavender"
              style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }}
              title="Edit task details"
            >
              <Edit3 size={13} />
              <span>Edit</span>
            </button>

            <button
              onClick={() => onDelete(todo.id)}
              className="neo-btn neo-btn-danger"
              style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem' }}
              title="Delete task"
            >
              <Trash2 size={13} />
              <span>Delete</span>
            </button>
          </div>

        </div>

      </div>
    </article>
  );
};
