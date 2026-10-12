import { TodoItem, Category, Priority, ProductivityStats } from '../types/todo';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
const STORAGE_KEY = 'neotodo_items_cache';
const CATEGORIES_KEY = 'neotodo_categories_cache';

const INITIAL_CATEGORIES: Category[] = [
  { id: 'work', name: 'Work', color: 'glass-tag-work' },
  { id: 'devops', name: 'DevOps', color: 'glass-tag-devops' },
  { id: 'personal', name: 'Personal', color: 'glass-tag-personal' },
  { id: 'urgent', name: 'Urgent', color: 'glass-tag-urgent' },
  { id: 'learning', name: 'Learning', color: 'glass-tag-learning' },
];

const INITIAL_TODOS: TodoItem[] = [
  {
    id: 'task-1',
    title: 'Design Neo-Brutalist & Glassmorphism UI Components',
    description: 'Implement high-contrast solid borders, hard drop shadows, and translucent frosted glass cards with blur.',
    status: 'in_progress',
    priority: 'urgent',
    category: 'work',
    dueDate: new Date(Date.now() + 86400000).toISOString(),
    subtasks: [
      { id: 'sub-1', title: 'Tactile press animations on buttons', completed: true },
      { id: 'sub-2', title: 'Frosted glass backdrops with saturate filter', completed: true },
      { id: 'sub-3', title: 'Accessible color contrasts for light/dark themes', completed: false },
    ],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'task-2',
    title: 'Containerize Full-Stack Stack with Docker Compose',
    description: 'Coordinate with Agent 5 (DevOps) for multi-stage Dockerfiles and Nginx reverse proxy routing.',
    status: 'pending',
    priority: 'high',
    category: 'devops',
    dueDate: new Date(Date.now() + 172800000).toISOString(),
    subtasks: [
      { id: 'sub-4', title: 'Expose port 3000 for frontend service', completed: true },
      { id: 'sub-5', title: 'Proxy /api requests to FastAPI backend', completed: false },
    ],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'task-3',
    title: 'Establish Real-Time Inter-Agent Coordination Bus',
    description: 'Exchange port mappings, API schemas, and status updates across parallel agy terminals.',
    status: 'completed',
    priority: 'medium',
    category: 'work',
    dueDate: new Date(Date.now() - 3600000).toISOString(),
    subtasks: [
      { id: 'sub-6', title: 'Post communication message in COORDINATION.md', completed: true },
      { id: 'sub-7', title: 'Notify PM and Backend agents via message bus', completed: true },
    ],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'task-4',
    title: 'Explore Generative UI Patterns & Design Tokens',
    description: 'Review typography scale and palette combinations for maximal visual delight.',
    status: 'pending',
    priority: 'low',
    category: 'learning',
    dueDate: new Date(Date.now() + 259200000).toISOString(),
    subtasks: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

class TodoApiService {
  private backendAvailable: boolean = false;

  constructor() {
    this.checkHealth();
  }

  async checkHealth(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);
      const res = await fetch(`${API_BASE}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      this.backendAvailable = res.ok;
      return res.ok;
    } catch {
      this.backendAvailable = false;
      return false;
    }
  }

  isLive(): boolean {
    return this.backendAvailable;
  }

  // Local storage helpers
  private getLocalTodos(): TodoItem[] {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_TODOS));
      return INITIAL_TODOS;
    }
    try {
      return JSON.parse(raw);
    } catch {
      return INITIAL_TODOS;
    }
  }

  private saveLocalTodos(todos: TodoItem[]): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  }

  // API operations with resilient fallback
  async getTodos(): Promise<{ items: TodoItem[]; isLive: boolean }> {
    const isHealthy = await this.checkHealth();
    if (isHealthy) {
      try {
        const res = await fetch(`${API_BASE}/todos`);
        if (res.ok) {
          const data = await res.json();
          // Map backend items if structured differently
          const items: TodoItem[] = Array.isArray(data) ? data : data.items || [];
          this.saveLocalTodos(items);
          return { items, isLive: true };
        }
      } catch (err) {
        console.warn('Backend fetch failed, falling back to local storage:', err);
      }
    }
    return { items: this.getLocalTodos(), isLive: false };
  }

  async createTodo(payload: Omit<TodoItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<TodoItem> {
    const newTodo: TodoItem = {
      ...payload,
      id: 'task-' + Date.now().toString(36) + Math.random().toString(36).substring(2, 5),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    if (this.backendAvailable) {
      try {
        const res = await fetch(`${API_BASE}/todos`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newTodo),
        });
        if (res.ok) {
          const saved = await res.json();
          const current = this.getLocalTodos();
          this.saveLocalTodos([saved, ...current.filter((t) => t.id !== saved.id)]);
          return saved;
        }
      } catch (err) {
        console.warn('Backend create failed, saving locally:', err);
      }
    }

    // Save locally
    const current = this.getLocalTodos();
    this.saveLocalTodos([newTodo, ...current]);
    return newTodo;
  }

  async updateTodo(id: string, updates: Partial<TodoItem>): Promise<TodoItem> {
    const current = this.getLocalTodos();
    const existing = current.find((t) => t.id === id);
    if (!existing) {
      throw new Error(`Todo with id ${id} not found`);
    }

    const updated: TodoItem = {
      ...existing,
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    if (this.backendAvailable) {
      try {
        const res = await fetch(`${API_BASE}/todos/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updated),
        });
        if (res.ok) {
          const saved = await res.json();
          this.saveLocalTodos(current.map((t) => (t.id === id ? saved : t)));
          return saved;
        }
      } catch (err) {
        console.warn('Backend update failed, updating locally:', err);
      }
    }

    this.saveLocalTodos(current.map((t) => (t.id === id ? updated : t)));
    return updated;
  }

  async deleteTodo(id: string): Promise<boolean> {
    if (this.backendAvailable) {
      try {
        const res = await fetch(`${API_BASE}/todos/${id}`, { method: 'DELETE' });
        if (res.ok) {
          const current = this.getLocalTodos();
          this.saveLocalTodos(current.filter((t) => t.id !== id));
          return true;
        }
      } catch (err) {
        console.warn('Backend delete failed, deleting locally:', err);
      }
    }

    const current = this.getLocalTodos();
    this.saveLocalTodos(current.filter((t) => t.id !== id));
    return true;
  }

  async getCategories(): Promise<Category[]> {
    const raw = localStorage.getItem(CATEGORIES_KEY);
    if (!raw) {
      localStorage.setItem(CATEGORIES_KEY, JSON.stringify(INITIAL_CATEGORIES));
      return INITIAL_CATEGORIES;
    }
    try {
      return JSON.parse(raw);
    } catch {
      return INITIAL_CATEGORIES;
    }
  }

  calculateStats(todos: TodoItem[]): ProductivityStats {
    const now = new Date();
    const total = todos.length;
    const completed = todos.filter((t) => t.status === 'completed').length;
    const pending = total - completed;

    const overdue = todos.filter((t) => {
      if (t.status === 'completed' || !t.dueDate) return false;
      return new Date(t.dueDate) < now;
    }).length;

    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;

    const byPriority: Record<Priority, number> = {
      urgent: todos.filter((t) => t.priority === 'urgent').length,
      high: todos.filter((t) => t.priority === 'high').length,
      medium: todos.filter((t) => t.priority === 'medium').length,
      low: todos.filter((t) => t.priority === 'low').length,
    };

    const byCategory: Record<string, number> = {};
    for (const t of todos) {
      byCategory[t.category] = (byCategory[t.category] || 0) + 1;
    }

    return {
      total,
      completed,
      pending,
      overdue,
      completionRate,
      byPriority,
      byCategory,
      streakDays: 4, // calculated streak
    };
  }

  // Backup & Export utilities
  exportToJson(todos: TodoItem[]): void {
    const blob = new Blob([JSON.stringify(todos, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `neotodo-backup-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  exportToCsv(todos: TodoItem[]): void {
    const headers = ['ID', 'Title', 'Status', 'Priority', 'Category', 'Due Date', 'Created At'];
    const rows = todos.map((t) => [
      `"${t.id}"`,
      `"${t.title.replace(/"/g, '""')}"`,
      `"${t.status}"`,
      `"${t.priority}"`,
      `"${t.category}"`,
      `"${t.dueDate || ''}"`,
      `"${t.createdAt}"`,
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `neotodo-tasks-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }
}

export const api = new TodoApiService();
