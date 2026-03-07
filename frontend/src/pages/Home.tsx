import { useQuery } from '@tanstack/react-query';
import { listDeals } from '../api/deals';
import { DealCard } from '../components/DealCard';
import { Spinner } from '../components/Spinner';

export const Home: React.FC = () => {
  const { data: deals, isLoading, error } = useQuery({
    queryKey: ['deals'],
    queryFn: listDeals,
  });

  if (isLoading) return <Spinner />;

  if (error) {
    return <div className="text-center py-8 text-red-500">Error loading deals</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8">Group Buy Deals</h1>

      {!deals || deals.length === 0 ? (
        <p className="text-gray-500">No deals available</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {deals.map(deal => (
            <DealCard key={deal.id} deal={deal} />
          ))}
        </div>
      )}
    </div>
  );
};