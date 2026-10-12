import React from 'react';
import { Search, ArrowUpDown, X } from 'lucide-react';
import { FilterStatus, Priority, Category, SortField, SortOrder } from '../types/todo';

interface FilterToolbarProps {
  statusFilter: FilterStatus;
  onStatusChange: (status: FilterStatus) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  priorityFilter: string;
  onPriorityChange: (p: string) => void;
  categoryFilter: string;
  onCategoryChange: (c: string) => void;
  categories: Category[];
  sortField: SortField;
  sortOrder: SortOrder;
  onSortChange: (field: SortField, order: SortOrder) => void;
  counts: {
    all: number;
    active: number;
    completed: number;
    overdue: number;
  };
}

export const FilterToolbar: React.FC<FilterToolbarProps> = ({
  statusFilter,
  onStatusChange,
  searchQuery,
  onSearchChange,
  priorityFilter,
  onPriorityChange,
  categoryFilter,
  onCategoryChange,
  categories,
  sortField,
  sortOrder,
  onSortChange,
  counts,
}) => {
  const statusTabs: { id: FilterStatus; label: string; count: number }[] = [
    { id: 'all', label: 'All Tasks', count: counts.all },
    { id: 'active', label: 'Active', count: counts.active },
    { id: 'completed', label: 'Completed', count: counts.completed },
    { id: 'overdue', label: 'Overdue', count: counts.overdue },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
      
      {/* Top Row: Status Tabs + Search */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '0.85rem' }}>
        
        {/* Status Buttons */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {statusTabs.map((tab) => {
            const isSelected = statusFilter === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onStatusChange(tab.id)}
                className={`neo-btn ${isSelected ? 'neo-btn-primary' : ''}`}
                style={{
                  padding: '0.45rem 0.85rem',
                  fontSize: '0.85rem',
                  fontWeight: isSelected ? 800 : 600,
                  boxShadow: isSelected ? 'var(--shadow-md)' : 'var(--shadow-sm)',
                  transform: isSelected ? 'translate(-1px, -1px)' : 'none',
                }}
              >
                <span>{tab.label}</span>
                <span
                  style={{
                    fontSize: '0.75rem',
                    padding: '0.1rem 0.45rem',
                    borderRadius: '9999px',
                    border: '1px solid var(--border-color)',
                    background: isSelected ? '#ffffff' : 'rgba(0,0,0,0.06)',
                    color: '#0f172a',
                    fontWeight: 800,
                  }}
                >
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search Bar */}
        <div style={{ position: 'relative', minWidth: '240px', flex: '1 1 260px', maxWidth: '380px' }}>
          <Search
            size={16}
            style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }}
          />
          <input
            type="text"
            className="neo-input"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Filter tasks by name or note..."
            style={{ paddingLeft: '36px', paddingRight: searchQuery ? '32px' : '12px' }}
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: 'var(--text-dim)',
              }}
            >
              <X size={14} />
            </button>
          )}
        </div>

      </div>

      {/* Bottom Filter & Sort Bar */}
      <div
        className="neo-box"
        style={{
          padding: '0.75rem 1rem',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '0.75rem',
          background: 'var(--glass-card)',
        }}
      >
        
        {/* Categories Pills */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.45rem' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-dim)', marginRight: '0.25rem' }}>
            Category:
          </span>
          <button
            onClick={() => onCategoryChange('all')}
            className={`neo-badge ${categoryFilter === 'all' ? 'neo-btn-mint' : ''}`}
            style={{ cursor: 'pointer', background: categoryFilter === 'all' ? 'var(--glass-mint)' : 'transparent' }}
          >
            All
          </button>
          {categories.map((c) => (
            <button
              key={c.id}
              onClick={() => onCategoryChange(c.id)}
              className={`neo-badge ${c.color}`}
              style={{
                cursor: 'pointer',
                borderWidth: categoryFilter === c.id ? '2.5px' : '1.5px',
                transform: categoryFilter === c.id ? 'scale(1.05)' : 'none',
                opacity: categoryFilter !== 'all' && categoryFilter !== c.id ? 0.6 : 1,
              }}
            >
              {c.name}
            </button>
          ))}
        </div>

        {/* Priority & Sorting */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          
          {/* Priority Select */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-dim)' }}>
              Priority:
            </span>
            <select
              value={priorityFilter}
              onChange={(e) => onPriorityChange(e.target.value)}
              className="neo-input"
              style={{ width: 'auto', padding: '0.25rem 0.6rem', fontSize: '0.8rem', fontWeight: 700 }}
            >
              <option value="all">All</option>
              <option value="urgent">Urgent</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          {/* Sort Control */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-dim)' }}>
              Sort:
            </span>
            <select
              value={sortField}
              onChange={(e) => onSortChange(e.target.value as SortField, sortOrder)}
              className="neo-input"
              style={{ width: 'auto', padding: '0.25rem 0.6rem', fontSize: '0.8rem', fontWeight: 700 }}
            >
              <option value="dueDate">Due Date</option>
              <option value="priority">Priority</option>
              <option value="createdAt">Date Created</option>
              <option value="title">Alphabetical</option>
            </select>
            <button
              onClick={() => onSortChange(sortField, sortOrder === 'asc' ? 'desc' : 'asc')}
              className="neo-btn"
              style={{ padding: '0.25rem 0.45rem' }}
              title={`Toggle sort direction (currently ${sortOrder.toUpperCase()})`}
            >
              <ArrowUpDown size={14} />
            </button>
          </div>

        </div>

      </div>

    </div>
  );
};
