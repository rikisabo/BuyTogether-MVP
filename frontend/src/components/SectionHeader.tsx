import React from 'react';

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  className?: string;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({ title, subtitle, className }) => (
  <div className={`mb-6 ${className ?? ''}`}>
    <h2 className="text-2xl md:text-3xl font-extrabold text-slate-800 mb-1">{title}</h2>
    {subtitle && <p className="text-sm md:text-base text-slate-500">{subtitle}</p>}
  </div>
);
