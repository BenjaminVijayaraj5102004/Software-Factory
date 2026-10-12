export type Priority = 'urgent' | 'high' | 'medium' | 'low';
export type TodoStatus = 'pending' | 'in_progress' | 'completed';

export interface Subtask {
  id: string;
  title: string;
  completed: boolean;
}

export interface Category {
  id: string;
  name: string;
  color: string; // glass color class or hex
}

export interface TodoItem {
  id: string;
  title: string;
  description?: string;
  status: TodoStatus;
  priority: Priority;
  category: string;
  dueDate?: string;
  subtasks: Subtask[];
  createdAt: string;
  updatedAt: string;
}

export type FilterStatus = 'all' | 'active' | 'completed' | 'overdue';
export type SortField = 'dueDate' | 'priority' | 'createdAt' | 'title';
export type SortOrder = 'asc' | 'desc';

export interface ProductivityStats {
  total: number;
  completed: number;
  pending: number;
  overdue: number;
  completionRate: number;
  byPriority: Record<Priority, number>;
  byCategory: Record<string, number>;
  streakDays: number;
}
