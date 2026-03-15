import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listDeals, DealsPage } from '../api/deals';
import { DealCard } from '../components/DealCard';
import { Spinner } from '../components/Spinner';
import { PageContainer } from '../components/PageContainer';
import { SectionHeader } from '../components/SectionHeader';
import { SearchFilterBar } from '../components/SearchFilterBar';

export const Home: React.FC = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'ALL' | 'ACTIVE' | 'NEW' | 'CLOSE' | 'TREND'>('ALL');
  const pageSize = 9; // show 9 cards per page

  const {
    data,
    isLoading,
    error,
  } = useQuery<DealsPage, unknown>({
    queryKey: ['deals', page],
    queryFn: () => listDeals({ status: filter === 'ALL' ? 'ACTIVE' : 'ACTIVE', page, page_size: pageSize }),
    keepPreviousData: true,
  });

  const deals = data?.items || [];
  const filteredDeals = useMemo(() => {
    const term = search.trim();
    let base = [...deals];
    if (filter === 'NEW') {
      base = deals.filter((d) => d.current_qty <= 5);
    }
    if (filter === 'CLOSE') {
      base = deals.filter((d) => d.current_qty >= d.min_qty_to_close * 0.7 && d.status === 'ACTIVE');
    }
    if (filter === 'TREND') {
      base = [...base].sort((a, b) => b.current_qty - a.current_qty);
    }

    if (!term) return base;

    return base.filter((d) =>
      d.title.includes(term) || (d.description ?? '').includes(term)
    );
  }, [deals, search, filter]);

  if (isLoading) return <div className="min-h-[60vh] flex items-center justify-center"><Spinner /></div>;

  if (error) {
    return <div className="text-center py-8 text-red-600">שגיאה בטעינת המבצעים, נסה שוב מאוחר יותר</div>;
  }

  return (
    <PageContainer className="space-y-8">
      <section className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-3xl p-8 shadow-xl">
        <h1 className="text-4xl md:text-5xl font-black mb-4">נקנה ביחד, נהנה ביחד</h1>
        <p className="text-lg md:text-xl text-indigo-100 max-w-2xl leading-relaxed">
          מציאת מחירים קבוצה לקנייה חכמה בישראל. הצטרפו לכמות הנדרשת, קבלו סוף סוף מחיר אמיתי.
        </p>
        <div className="mt-6 flex flex-col sm:flex-row gap-3">
          <a href="#deals" className="inline-flex items-center justify-center px-6 py-3 bg-white text-indigo-700 rounded-xl font-bold shadow-md hover:shadow-lg transition">
            צפה במבצעים פעילים
          </a>
          <span className="inline-flex items-center rounded-xl bg-white/10 px-4 py-2 text-sm text-white">נשארו כרגע {data?.total ?? 0} מבצעים פעילים</span>
        </div>
      </section>

      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
        <SectionHeader title="מבצעים פעילים" subtitle="בחרו את המבצע שהכי מתאים לכם" />
        <SearchFilterBar search={search} onSearchChange={setSearch} activeFilter={filter} onFilterChange={setFilter} />

        {filteredDeals.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-2xl font-semibold text-slate-700">אין מבצעים תואמים</p>
            <p className="text-slate-500 mt-2">נסו להרחיב את החיפוש או לשנות את המסנן</p>
          </div>
        ) : (
          <>
            <div id="deals" className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredDeals.map((deal) => (
                <DealCard key={deal.id} deal={deal} />
              ))}
            </div>

            <div className="flex justify-center items-center gap-3 mt-7">
              <button
                className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50"
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
                disabled={page === 1}
              >
                קודם
              </button>
              <span className="text-slate-600">
                דף {page} מתוך {data ? Math.ceil(data.total / pageSize) : 1}
              </span>
              <button
                className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 disabled:opacity-50"
                onClick={() => {
                  if (data && page * pageSize < data.total) {
                    setPage((p) => p + 1);
                  }
                }}
                disabled={!data || page * pageSize >= data.total}
              >
                הבא
              </button>
            </div>
          </>
        )}
      </div>
    </PageContainer>
  );
};