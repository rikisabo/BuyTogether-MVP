import { Link } from 'react-router-dom';
import { Deal } from '../api/deals';
import { formatStatus, calculatePercent } from '../lib/format';
import { ProgressBar } from './ProgressBar';
import { StatusBadge } from './StatusBadge';
import { CountdownTimer } from './CountdownTimer';

interface DealCardProps {
  deal: Deal;
}

export const DealCard: React.FC<DealCardProps> = ({ deal }) => {
  const image = deal.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80';
  const remaining = Math.max(deal.min_qty_to_close - deal.current_qty, 0);
  const progress = calculatePercent(deal.current_qty, deal.min_qty_to_close);

  const mockRating = 4.7;
  const mockReviews = 23;
  const tags = [] as string[];
  if (deal.current_qty > deal.min_qty_to_close * 0.8) tags.push('כמעט נסגר');
  if (deal.current_qty >= deal.min_qty_to_close) tags.push('🔥 בערימה');
  if (!deal.image_url) tags.push('חדש');

  return (
    <Link to={`/deals/${deal.id}`} className="group">
      <article className="bg-white rounded-2xl shadow-sm hover:shadow-xl transition duration-300 overflow-hidden border border-transparent hover:border-indigo-100">
        <div className="relative h-52 lg:h-48 bg-slate-100 overflow-hidden">
          <img src={image} alt={deal.title} className="w-full h-full object-cover object-center transition-transform duration-500 group-hover:scale-105" />
          <div className="absolute top-3 right-3 flex flex-col gap-1">
            <StatusBadge status={deal.status} />
            {deal.status === 'ACTIVE' && <CountdownTimer endDate={deal.end_at} />}
          </div>
        </div>

        <div className="p-4 space-y-3">
          <div className="flex justify-between items-center">
            <h3 className="text-xl font-bold text-slate-800">{deal.title}</h3>
          </div>

          <p className="text-sm text-slate-500 line-clamp-2">{deal.description || 'מבצע קנייה קבוצתית אטרקטיבי במיוחד למוצרים מובילים'} </p>

          <div className="flex gap-2 flex-wrap">
            {tags.map(tag => (
              <span key={tag} className="text-xs font-bold bg-emerald-50 text-emerald-700 rounded-full px-2 py-1">{tag}</span>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="text-xs text-slate-500">מחיר ליחידה</div>
              <div className="text-lg font-bold">₪{(deal.price_cents / 100).toFixed(2)}</div>
            </div>
            <div>
              <div className="text-xs text-slate-500">תמיכה</div>
              <div className="text-lg font-bold">{deal.current_qty}/{deal.min_qty_to_close}</div>
            </div>
          </div>

          <ProgressBar current={deal.current_qty} target={deal.min_qty_to_close} />

          <p className="text-xs text-slate-500">נשארו {remaining} ליעד</p>

          <div className="flex items-center justify-between text-xs text-slate-600">
            <span>⭐ {mockRating} ({mockReviews} חוות דעת)</span>
            <span className="font-semibold">{progress}%</span>
          </div>

          <button className="w-full text-center bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl py-2 font-semibold transition">לפרטי מבצע</button>
        </div>
      </article>
    </Link>
  );
};