import { useEffect, useState } from 'react';

interface CountdownTimerProps {
  endDate: string;
}

const pad = (num: number) => num.toString().padStart(2, '0');

export const CountdownTimer: React.FC<CountdownTimerProps> = ({ endDate }) => {
  const [timeLeft, setTimeLeft] = useState('');

  useEffect(() => {
    const target = new Date(endDate).getTime();
    if (Number.isNaN(target)) {
      setTimeLeft('תאריך לא תקין');
      return;
    }

    const update = () => {
      const now = Date.now();
      const diff = target - now;
      if (diff <= 0) {
        setTimeLeft('העסקה הסתיימה');
        return;
      }
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const secs = Math.floor((diff % (1000 * 60)) / 1000);
      setTimeLeft(`${days} ימים ${pad(hours)}:${pad(mins)}:${pad(secs)}`);
    };

    update();
    const intervalId = setInterval(update, 1000);
    return () => clearInterval(intervalId);
  }, [endDate]);

  return (
    <div className="inline-flex items-center gap-2 bg-indigo-50 border border-indigo-100 text-indigo-700 rounded-full px-3 py-1 text-sm font-semibold">
      <span>העסקה מסתיימת בעוד</span>
      <span className="font-bold">{timeLeft}</span>
    </div>
  );
};
