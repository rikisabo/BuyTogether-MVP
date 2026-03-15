import React from 'react';

interface SearchFilterBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  activeFilter: 'ALL' | 'ACTIVE' | 'CLOSE' | 'NEW' | 'TREND';
  onFilterChange: (filter: 'ALL' | 'ACTIVE' | 'CLOSE' | 'NEW' | 'TREND') => void;
}

const filters = [
  { key: 'ALL', label: 'הכל' },
  { key: 'ACTIVE', label: 'פעילים' },
  { key: 'NEW', label: 'חדשים' },
  { key: 'CLOSE', label: 'כמעט נסגרים' },
  { key: 'TREND', label: 'פופולריים' },
] as const;

export const SearchFilterBar: React.FC<SearchFilterBarProps> = ({ search, onSearchChange, activeFilter, onFilterChange }) => {
  return (
    <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100 mb-6 transition-all">
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="חפש מבצעים, מוצר, מותג..."
          className="w-full sm:max-w-md border border-slate-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <div className="flex flex-wrap gap-2">
          {filters.map(f => (
            <button
              key={f.key}
              type="button"
              onClick={() => onFilterChange(f.key as any)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium ${activeFilter === f.key ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
