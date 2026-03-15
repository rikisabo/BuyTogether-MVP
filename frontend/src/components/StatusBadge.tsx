import React from 'react';

type Status = 'ACTIVE' | 'CLOSED' | 'COMPLETED' | 'FAILED' | string;

const mapStatus = {
  ACTIVE: { text: 'פעילה', className: 'bg-emerald-100 text-emerald-700' },
  CLOSED: { text: 'נסגרה', className: 'bg-orange-100 text-orange-700' },
  COMPLETED: { text: 'הושלמה', className: 'bg-blue-100 text-blue-700' },
  FAILED: { text: 'נכשלה', className: 'bg-red-100 text-red-700' },
};

interface StatusBadgeProps {
  status: Status;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const entry = (mapStatus as any)[status] || { text: status || 'לא ידוע', className: 'bg-gray-200 text-slate-700' };
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold tracking-wide ${entry.className}`}>
      {entry.text}
    </span>
  );
};
