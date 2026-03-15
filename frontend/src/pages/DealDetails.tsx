import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getDeal } from '../api/deals';
import { calculatePercent } from '../lib/format';
import { ProgressBar } from '../components/ProgressBar';
import { JoinForm } from '../components/JoinForm';
import { Spinner } from '../components/Spinner';
import { PageContainer } from '../components/PageContainer';
import { StatusBadge } from '../components/StatusBadge';
import { CountdownTimer } from '../components/CountdownTimer';
import { SectionHeader } from '../components/SectionHeader';

export const DealDetails: React.FC = () => {
  const { dealId } = useParams<{ dealId: string }>();

  if (!dealId) {
    return <div className="text-red-500">Invalid deal ID</div>;
  }

  const { data: deal, isLoading, error } = useQuery({
    queryKey: ['deal', dealId],
    queryFn: () => getDeal(dealId),
  });

  if (isLoading) return <div className="min-h-[60vh] flex items-center justify-center"><Spinner /></div>;

  if (error || !deal) {
    return <div className="text-center py-8 text-red-500">Error loading deal</div>;
  }

  const completion = calculatePercent(deal.current_qty, deal.min_qty_to_close);
  const remaining = Math.max(deal.min_qty_to_close - deal.current_qty, 0);

  return (
    <PageContainer>
      <div className="grid gap-8 lg:grid-cols-[1.6fr_1fr] items-start">
        <article className="bg-white rounded-2xl shadow-lg overflow-hidden border border-slate-200">
          <div className="relative h-96 bg-slate-100 overflow-hidden">
            <img
              src={deal.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1500&q=80'}
              alt={deal.title}
              className="w-full h-full object-cover object-center"
            />
            <div className="absolute top-4 left-4 text-sm bg-black/40 text-white rounded-md px-3 py-1">תצוגה מוקדמת</div>
          </div>
          <section className="p-6 space-y-4">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <h1 className="text-3xl font-extrabold text-slate-900">{deal.title}</h1>
              <StatusBadge status={deal.status} />
            </div>

            <p className="text-slate-600 leading-relaxed">{deal.description ?? 'מבצע קנייה קבוצתית עם תמיכה מלאה וניהול אוטומטי שיעלה את רמת החיסכון.'}</p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="bg-slate-50 rounded-xl p-4 text-slate-700">
                <div className="text-xs">מחיר ליחידה</div>
                <div className="text-2xl font-bold">₪{(deal.price_cents / 100).toFixed(2)}</div>
              </div>
              <div className="bg-slate-50 rounded-xl p-4 text-slate-700">
                <div className="text-xs">כמות נוכחית</div>
                <div className="text-2xl font-bold">{deal.current_qty}/{deal.min_qty_to_close}</div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3"> 
              <CountdownTimer endDate={deal.end_at} />
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 text-sm font-semibold">{completion}% הושלם</div>
            </div>

            <div className="py-3">
              <ProgressBar current={deal.current_qty} target={deal.min_qty_to_close} />
              <p className="text-sm text-slate-500 mt-2">נשארו עוד {remaining} כדי להשלים את היעד ולסגור את המחיר.</p>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm text-slate-600">
              <div>⭐ 4.7 (24 חוות דעת)</div>
              <div>🛍 73% משתמשים מרוצים</div>
              <div>🔥 מבצע מוביל</div>
              <div>🚚 משלוח חינם לאחר סגירה</div>
            </div>
          </section>
        </article>

        <aside className="space-y-4">
          <section className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <h2 className="text-2xl font-bold mb-3">הצטרפות</h2>
            {deal.status === 'ACTIVE' ? (
              <JoinForm dealId={dealId} isActive />
            ) : (
              <div className="rounded-xl bg-slate-50 p-4 text-slate-700">
                <p className="font-semibold">המבצע סגור</p>
                <p>כרגע לא ניתן להצטרף. בדוק את העמוד הראשי למבצעים פעילים נוספים.</p>
              </div>
            )}
          </section>

          <section className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <h2 className="text-xl font-semibold mb-3">פרטי המבצע</h2>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>⏳ סיום: {new Date(deal.end_at).toLocaleString('he-IL')}</li>
              <li>👥 משתתפים: {deal.participants_count ?? deal.current_qty}</li>
              <li>📦 משלוח: עם משלוח שרוכה לאחר סגירה</li>
              <li>🔄 ביטול: ניתן לבטל בתוך 24 שעות</li>
            </ul>
          </section>
        </aside>
      </div>

      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm mt-8">
        <SectionHeader title="למה לבחור בקנייה קבוצתית?" subtitle="יותר שוויון, פחות עלויות" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-slate-700">
          <div className="bg-indigo-50 p-4 rounded-xl">חיסכון משמעותי בעשרות אחוזים על המחיר הקמעונאי.</div>
          <div className="bg-indigo-50 p-4 rounded-xl">תהליך שקוף עם עדכונים בזמן אמת בכל שלב.</div>
          <div className="bg-indigo-50 p-4 rounded-xl">מעל 300 הצטרפים פעילים ברחבי הארץ.</div>
          <div className="bg-indigo-50 p-4 rounded-xl">משלוח מתואם לכל הכתובות הנבחרות.</div>
        </div>
      </section>

      <section className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm mt-6">
        <SectionHeader title="שאלות נפוצות" />
        <div className="space-y-3 text-slate-700 text-sm">
          <div>
            <p className="font-semibold">איך אני משלם?</p>
            <p>קישור תשלום נשלח רק לאחר שהמבצע נסגר בהצלחה.</p>
          </div>
          <div>
            <p className="font-semibold">מה קורה אם המחיר לא ננעל?</p>
            <p>אם לא מגיעים ליעד, התשלום אינו מחוייב והקבוצה לא תעמוד.</p>
          </div>
          <div>
            <p className="font-semibold">איך אני אקבל עדכונים?</p>
            <p>עידכונים נשלחים למייל ודף ההצעיות יתעדכן בזמן אמת.</p>
          </div>
        </div>
      </section>
    </PageContainer>
  );
};