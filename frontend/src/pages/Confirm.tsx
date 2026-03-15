import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { client } from '../api/client';
import { Spinner } from '../components/Spinner';
import { PageContainer } from '../components/PageContainer';

export const Confirm: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    if (token) {
      client
        .post(`/confirm/${token}`)
        .then((res) => {
          if (res.data.data.success) setStatus('success');
          else setStatus('error');
        })
        .catch(() => setStatus('error'));
    } else {
      setStatus('error');
    }
  }, [token]);

  if (status === 'loading') return <div className="min-h-[60vh] flex items-center justify-center"><Spinner /></div>;

  return (
    <PageContainer>
      <div className="max-w-md mx-auto text-center bg-white p-8 rounded-2xl shadow-lg border border-slate-200">
        {status === 'success' ? (
          <>
            <p className="text-3xl font-black text-emerald-700 mb-4">✅ אישרת בהצלחה</p>
            <p className="text-slate-600">הצטרפותך נשמרה. בקרוב נשלח עדכון על סטטוס הקבוצה.</p>
          </>
        ) : (
          <>
            <p className="text-3xl font-black text-red-700 mb-4">❌ קישור לא תקין</p>
            <p className="text-slate-600">הקישור שפג תוקפו או אינו קיים. חזור לדף המבצע ונסה שוב.</p>
          </>
        )}
      </div>
    </PageContainer>
  );
};