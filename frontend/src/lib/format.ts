export const formatStatus = (status: string): string => {
  return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
};

export const calculatePercent = (current: number, target: number | null): number => {
  if (!target || target === 0) return 0;
  return Math.min((current / target) * 100, 100);
};