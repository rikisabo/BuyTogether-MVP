import { calculatePercent } from '../lib/format';

interface ProgressBarProps {
  current: number;
  target: number | null;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ current, target }) => {
  const percent = calculatePercent(current, target);

  return (
    <div className="w-full">
      <div className="bg-gray-200 rounded h-2 overflow-hidden">
        <div
          className="bg-blue-500 h-full transition-all"
          style={{ width: `${percent}%` }}
        ></div>
      </div>
      <p className="text-sm text-gray-600 mt-1">
        {current}/{target || '∞'} qty
      </p>
    </div>
  );
};