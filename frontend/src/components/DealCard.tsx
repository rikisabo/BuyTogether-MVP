import { Link } from 'react-router-dom';
import { Deal } from '../api/deals';
import { formatStatus } from '../lib/format';
import { ProgressBar } from './ProgressBar';

interface DealCardProps {
  deal: Deal;
}

export const DealCard: React.FC<DealCardProps> = ({ deal }) => {
  return (
    <Link to={`/deals/${deal.id}`}>
      <div className="bg-white p-6 rounded shadow hover:shadow-lg transition-shadow cursor-pointer">
        <h3 className="font-bold text-lg mb-2">{deal.title}</h3>
        <p className="text-sm text-gray-600 mb-4">
          Status: <span className={`font-semibold ${deal.status === 'ACTIVE' ? 'text-green-600' : 'text-gray-600'}`}>
            {formatStatus(deal.status)}
          </span>
        </p>
        <div className="mb-4">
          <ProgressBar current={deal.current_qty} target={deal.min_qty_to_close} />
        </div>
        <p className="text-xs text-gray-500">Price: ¢{deal.price_cents}</p>
      </div>
    </Link>
  );
};