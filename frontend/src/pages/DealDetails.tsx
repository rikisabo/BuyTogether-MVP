import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getDeal } from '../api/deals';
import { formatStatus, calculatePercent } from '../lib/format';
import { ProgressBar } from '../components/ProgressBar';
import { JoinForm } from '../components/JoinForm';
import { Spinner } from '../components/Spinner';

export const DealDetails: React.FC = () => {
  const { dealId } = useParams<{ dealId: string }>();

  if (!dealId) {
    return <div className="text-red-500">Invalid deal ID</div>;
  }

  const { data: deal, isLoading, error } = useQuery({
    queryKey: ['deal', dealId],
    queryFn: () => getDeal(dealId),
  });

  if (isLoading) return <Spinner />;

  if (error || !deal) {
    return <div className="text-center py-8 text-red-500">Error loading deal</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">{deal.title}</h1>

        <div className="bg-white p-6 rounded shadow mb-8">
          <p className="text-sm text-gray-600 mb-2">
            Status: <span className={`font-semibold ${deal.status === 'ACTIVE' ? 'text-green-600' : 'text-gray-600'}`}>
              {formatStatus(deal.status)}
            </span>
          </p>

          {deal.description && (
            <p className="text-gray-700 mb-4">{deal.description}</p>
          )}

          <div className="mb-6">
            <h2 className="font-semibold mb-2">Progress</h2>
            <ProgressBar current={deal.current_qty} target={deal.min_qty_to_close} />
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm mb-6">
            <div>
              <p className="text-gray-600">Price per Unit</p>
              <p className="font-semibold">¢{deal.price_cents}</p>
            </div>
            <div>
              <p className="text-gray-600">Completion</p>
              <p className="font-semibold">{Math.round(calculatePercent(deal.current_qty, deal.min_qty_to_close))}%</p>
            </div>
          </div>

          {deal.image_url && (
            <img src={deal.image_url} alt={deal.title} className="w-full rounded mb-4" />
          )}
        </div>

        <JoinForm dealId={dealId} isActive={deal.status === 'ACTIVE'} />
      </div>
    </div>
  );
};