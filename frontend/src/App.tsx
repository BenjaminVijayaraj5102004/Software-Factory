import React, { useState, useEffect, useMemo } from 'react';
import { Header } from './components/Header';
import { TaskCreator } from './components/TaskCreator';
import { FilterToolbar } from './components/FilterToolbar';
import { TodoCard } from './components/TodoCard';
import { EditTaskModal } from './components/EditTaskModal';
import { AnalyticsModal } from './components/AnalyticsModal';
import { Toast, ToastMessage } from './components/Toast';
import { api } from './services/api';
import {
  TodoItem,
  Subtask,
  Category,
  FilterStatus,
  SortField,
  SortOrder,
  Priority,
  ProductivityStats,
} from './types/todo';

export const App: React.FC = () => {
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLive, setIsLive] = useState<boolean>(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Filters & Search
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('dueDate');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  // Modals & Feedback
  const [editingTodo, setEditingTodo] = useState<TodoItem | null>(null);
  const [isAnalyticsOpen, setIsAnalyticsOpen] = useState<boolean>(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Toast Helper
  const addToast = (text: string, type: 'success' | 'info' | 'warning' = 'success') => {
    const id = Date.now().toString(36) + Math.random().toString(36).substring(2, 4);
    setToasts((prev) => [...prev, { id, text, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3200);
  };

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Theme Sync
  useEffect(() => {
    const saved = localStorage.getItem('neotodo_theme') as 'light' | 'dark';
    if (saved) {
      setTheme(saved);
      document.documentElement.setAttribute('data-theme', saved);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  }, []);

  const toggleTheme = () => {
    const next = theme === 'light' ? 'dark' : 'light';
    setTheme(next);
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('neotodo_theme', next);
    addToast(`Switched to ${next} theme`, 'info');
  };

  // Initial Fetch & Periodic Sync
  useEffect(() => {
    const loadData = async () => {
      const [todosRes, catRes] = await Promise.all([api.getTodos(), api.getCategories()]);
      setTodos(todosRes.items);
      setIsLive(todosRes.isLive);
      setCategories(catRes);
    };
    loadData();

    // Check health periodically
    const healthInterval = setInterval(async () => {
      const live = await api.checkHealth();
      setIsLive(live);
    }, 15000);
    return () => clearInterval(healthInterval);
  }, []);

  // Productivity Stats
  const stats: ProductivityStats = useMemo(() => {
    return api.calculateStats(todos);
  }, [todos]);

  // Tab Counts
  const counts = useMemo(() => {
    const now = new Date();
    return {
      all: todos.length,
      active: todos.filter((t) => t.status !== 'completed').length,
      completed: todos.filter((t) => t.status === 'completed').length,
      overdue: todos.filter((t) => t.status !== 'completed' && t.dueDate && new Date(t.dueDate) < now)
        .length,
    };
  }, [todos]);

  // Filter & Sort Logic
  const filteredTodos = useMemo(() => {
    const now = new Date();
    return todos
      .filter((t) => {
        // Status filter
        if (statusFilter === 'active' && t.status === 'completed') return false;
        if (statusFilter === 'completed' && t.status !== 'completed') return false;
        if (statusFilter === 'overdue') {
          if (t.status === 'completed' || !t.dueDate || new Date(t.dueDate) >= now) return false;
        }

        // Category filter
        if (categoryFilter !== 'all' && t.category !== categoryFilter) return false;

        // Priority filter
        if (priorityFilter !== 'all' && t.priority !== priorityFilter) return false;

        // Search Query
        if (searchQuery.trim()) {
          const q = searchQuery.toLowerCase();
          const matchTitle = t.title.toLowerCase().includes(q);
          const matchDesc = t.description?.toLowerCase().includes(q);
          const matchSubtask = t.subtasks?.some((s: Subtask) => s.title.toLowerCase().includes(q));
          if (!matchTitle && !matchDesc && !matchSubtask) return false;
        }

        return true;
      })
      .sort((a, b) => {
        const priorityOrder: Record<Priority, number> = { urgent: 4, high: 3, medium: 2, low: 1 };
        let comparison = 0;

        if (sortField === 'dueDate') {
          const aTime = a.dueDate ? new Date(a.dueDate).getTime() : Infinity;
          const bTime = b.dueDate ? new Date(b.dueDate).getTime() : Infinity;
          comparison = aTime - bTime;
        } else if (sortField === 'priority') {
          comparison = priorityOrder[b.priority] - priorityOrder[a.priority];
        } else if (sortField === 'createdAt') {
          comparison = new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        } else if (sortField === 'title') {
          comparison = a.title.localeCompare(b.title);
        }

        return sortOrder === 'asc' ? comparison : -comparison;
      });
  }, [todos, statusFilter, categoryFilter, priorityFilter, searchQuery, sortField, sortOrder]);

  // Handlers
  const handleAddTask = async (data: {
    title: string;
    description?: string;
    priority: Priority;
    category: string;
    dueDate?: string;
  }) => {
    try {
      const created = await api.createTodo({
        ...data,
        status: 'pending',
        subtasks: [],
      });
      setTodos((prev) => [created, ...prev]);
      addToast(`Added: "${created.title}"`, 'success');
    } catch {
      addToast('Failed to save task', 'warning');
    }
  };

  const handleToggleStatus = async (id: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    try {
      const updated = await api.updateTodo(id, { status: nextStatus as any });
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)));
      addToast(
        nextStatus === 'completed' ? 'Completed task! 🎉' : 'Task restored to active',
        'info'
      );
    } catch {
      addToast('Could not update status', 'warning');
    }
  };

  const handleDeleteTask = async (id: string) => {
    try {
      await api.deleteTodo(id);
      setTodos((prev) => prev.filter((t) => t.id !== id));
      addToast('Task deleted', 'info');
    } catch {
      addToast('Could not delete task', 'warning');
    }
  };

  const handleSaveEdit = async (id: string, updates: Partial<TodoItem>) => {
    try {
      const updated = await api.updateTodo(id, updates);
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)));
      addToast('Changes saved successfully', 'success');
    } catch {
      addToast('Failed to save updates', 'warning');
    }
  };

  const handleAddSubtask = async (todoId: string, title: string) => {
    const todo = todos.find((t) => t.id === todoId);
    if (!todo) return;
    const newSubtask = {
      id: 'sub-' + Date.now().toString(36),
      title,
      completed: false,
    };
    const updatedSubtasks = [...todo.subtasks, newSubtask];
    const updated = await api.updateTodo(todoId, { subtasks: updatedSubtasks });
    setTodos((prev) => prev.map((t) => (t.id === todoId ? updated : t)));
  };

  const handleToggleSubtask = async (todoId: string, subtaskId: string, completed: boolean) => {
    const todo = todos.find((t) => t.id === todoId);
    if (!todo) return;
    const updatedSubtasks = todo.subtasks.map((s: Subtask) =>
      s.id === subtaskId ? { ...s, completed: !completed } : s
    );
    const updated = await api.updateTodo(todoId, { subtasks: updatedSubtasks });
    setTodos((prev) => prev.map((t) => (t.id === todoId ? updated : t)));
  };

  const handleDeleteSubtask = async (todoId: string, subtaskId: string) => {
    const todo = todos.find((t) => t.id === todoId);
    if (!todo) return;
    const updatedSubtasks = todo.subtasks.filter((s: Subtask) => s.id !== subtaskId);
    const updated = await api.updateTodo(todoId, { subtasks: updatedSubtasks });
    setTodos((prev) => prev.map((t) => (t.id === todoId ? updated : t)));
  };

  const handleExportJson = () => {
    api.exportToJson(todos);
    addToast('Downloaded JSON task backup', 'success');
  };

  const handleExportCsv = () => {
    api.exportToCsv(todos);
    addToast('Downloaded CSV spreadsheet', 'success');
  };

  return (
    <div style={{ maxWidth: '880px', margin: '0 auto', padding: '2rem 1.25rem 4rem 1.25rem' }}>
      
      {/* App Header */}
      <Header
        stats={stats}
        isLive={isLive}
        theme={theme}
        onToggleTheme={toggleTheme}
        onOpenAnalytics={() => setIsAnalyticsOpen(true)}
      />

      {/* Task Creation Hero Bar */}
      <TaskCreator categories={categories} onAddTask={handleAddTask} />

      {/* Filter & Search Toolbar */}
      <FilterToolbar
        statusFilter={statusFilter}
        onStatusChange={setStatusFilter}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        priorityFilter={priorityFilter}
        onPriorityChange={setPriorityFilter}
        categoryFilter={categoryFilter}
        onCategoryChange={setCategoryFilter}
        categories={categories}
        sortField={sortField}
        sortOrder={sortOrder}
        onSortChange={(field, order) => {
          setSortField(field);
          setSortOrder(order);
        }}
        counts={counts}
      />

      {/* Task List / Cards Container */}
      <main>
        {filteredTodos.length > 0 ? (
          filteredTodos.map((todo) => (
            <TodoCard
              key={todo.id}
              todo={todo}
              onToggleStatus={handleToggleStatus}
              onDelete={handleDeleteTask}
              onEdit={(t) => setEditingTodo(t)}
              onAddSubtask={handleAddSubtask}
              onToggleSubtask={handleToggleSubtask}
              onDeleteSubtask={handleDeleteSubtask}
            />
          ))
        ) : (
          <div
            className="neo-box"
            style={{
              padding: '3rem 1.5rem',
              textAlign: 'center',
              background: 'var(--glass-card)',
            }}
          >
            <div
              style={{
                width: '56px',
                height: '56px',
                borderRadius: '12px',
                border: '2.5px solid var(--border-color)',
                background: 'var(--glass-yellow)',
                margin: '0 auto 1rem auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.75rem',
                fontWeight: 900,
                color: '#0f172a',
              }}
            >
              ✦
            </div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '0.4rem' }}>
              No tasks found in this view
            </h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', maxWidth: '400px', margin: '0 auto 1.25rem auto' }}>
              {searchQuery
                ? `No tasks matched your query "${searchQuery}". Clear your search or adjust the filters.`
                : 'All caught up! Add a new task above or select another filter view.'}
            </p>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="neo-btn neo-btn-primary"
              >
                Clear Search Filter
              </button>
            )}
          </div>
        )}
      </main>

      {/* Modals */}
      {editingTodo && (
        <EditTaskModal
          todo={editingTodo}
          categories={categories}
          onSave={handleSaveEdit}
          onClose={() => setEditingTodo(null)}
        />
      )}

      {isAnalyticsOpen && (
        <AnalyticsModal
          stats={stats}
          todos={todos}
          onExportJson={handleExportJson}
          onExportCsv={handleExportCsv}
          onClose={() => setIsAnalyticsOpen(false)}
        />
      )}

      {/* Tactile Toasts */}
      <Toast toasts={toasts} onDismiss={dismissToast} />

    </div>
  );
};
export default App;
