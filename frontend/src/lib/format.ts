export const formatStatus = (status: string): string => {
  switch (status) {
    case 'ACTIVE':
      return 'פעיל';
    case 'CLOSED':
      return 'נסגר בהצלחה';
    case 'FAILED':
      return 'נכשל';
    default:
      return 'לא ידוע';
  }
};

export const calculatePercent = (current: number, target: number | null): number => {
  if (!target || target === 0) return 0;
  return Math.min((current / target) * 100, 100);
};

export const timeUntil = (iso: string): string => {
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return 'הסתיים';
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

  if (days > 0) return `${days} ימים`; 
  if (hours > 0) return `${hours} שעות`;
  return 'פחות משעה';
};