import { useState } from 'react';
import { useToast } from '../components/Toast';
import { PageContainer } from '../components/PageContainer';
import { CreateDealSchema, CreateDealPayload, createDeal, runCloseJob } from '../api/admin';
import { Spinner } from '../components/Spinner';
import { z } from 'zod';

// form state uses string for price_cents for easier typing
type AdminFormState = Omit<CreateDealPayload, 'price_cents'> & { price_cents: string };

export const Admin: React.FC = () => {
  const { showToast } = useToast();

  const [form, setForm] = useState<AdminFormState>({
    title: '',
    description: '',
    image_url: undefined,
    price_cents: '',
    min_qty_to_close: 1,
    end_at: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [jobResult, setJobResult] = useState<{ closed_count: number; failed_count: number } | null>(null);
  const [jobLoading, setJobLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: name === 'min_qty_to_close' ? Number(value) : value,
    }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    let parsed;
    try {
      parsed = CreateDealSchema.parse(form);
    } catch (err) {
      if (err instanceof z.ZodError) {
        const newErrors: Record<string, string> = {};
        err.errors.forEach(er => {
          if (er.path[0]) newErrors[er.path[0] as string] = er.message;
        });
        setErrors(newErrors);
        return;
      }
      throw err;
    }

    setIsSubmitting(true);
    try {
      await createDeal(parsed);
      showToast('המבצע נוצר בהצלחה', 'success');
      setForm({
        title: '',
        description: '',
        image_url: undefined,
        price_cents: '',
        min_qty_to_close: 1,
        end_at: '',
      });
      setErrors({});
    } catch (error: any) {
      // try to surface validation errors from the backend
      const msg =
        error.response?.data?.error?.message ||
        (error.response?.data?.error?.details &&
          error.response.data.error.details.map((d: any) => d.msg).join(', ')) ||
        error.message ||
        'Failed to create deal';
      if (error.response?.status === 422 && error.response.data?.error?.details) {
        const newErrors: Record<string, string> = {};
        error.response.data.error.details.forEach((er: any) => {
          if (er.loc && er.loc[0]) {
            newErrors[er.loc[0] as string] = er.msg;
          }
        });
        setErrors(newErrors);
      }
      showToast(msg || 'נכשל ביצירת המבצע, נסה שוב', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRunJob = async () => {
    setJobLoading(true);
    try {
      const res = await runCloseJob();
      setJobResult(res);
      showToast('Close job completed', 'success');
    } catch (error: any) {
      showToast(error.response?.data?.detail || 'Job failed', 'error');
    } finally {
      setJobLoading(false);
    }
  };

  return (
    <PageContainer>
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-lg border border-slate-200">
        <h1 className="text-4xl font-bold mb-4">לוח ניהול מבצעים</h1>

        <h2 className="text-2xl font-semibold mb-4">יצירת מבצע חדש</h2>
        <form onSubmit={handleSubmit} className="space-y-4 mb-8">
          <div>
            <label className="block text-sm font-medium mb-1">כותרת מבצע</label>
            <input
              name="title"
              value={form.title}
              onChange={handleChange}
              placeholder="סוללות של שיאומי ב-20% הנחה"
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
              disabled={isSubmitting}
            />
            {errors.title && <p className="text-red-500 text-xs mt-1">{errors.title}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">תיאור המבצע</label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              placeholder="לאחר השגת המינימום נשלחת הזמנה לביצוע תשלום."
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
              disabled={isSubmitting}
            />
            {errors.description && <p className="text-red-500 text-xs mt-1">{errors.description}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">מחיר (ש"ח)</label>
            <input
              type="text"
              inputMode="numeric"
              name="price_cents"
              value={form.price_cents}
              onChange={handleChange}
              placeholder="75"
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
              disabled={isSubmitting}
            />
            {errors.price_cents && <p className="text-red-500 text-xs mt-1">{errors.price_cents}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">כמות יעד</label>
            <input
              type="number"
              name="min_qty_to_close"
              value={form.min_qty_to_close}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
              disabled={isSubmitting}
            />
            {errors.min_qty_to_close && <p className="text-red-500 text-xs mt-1">{errors.min_qty_to_close}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">מועד סיום</label>
            <input
              type="datetime-local"
              name="end_at"
              value={form.end_at}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
              disabled={isSubmitting}
            />
            {errors.end_at && <p className="text-red-500 text-xs mt-1">{errors.end_at}</p>}
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:bg-gray-400"
          >
            {isSubmitting ? <Spinner /> : 'צור מבצע'}
          </button>
        </form>

        <h2 className="text-2xl font-semibold mb-4">הפעלה ידנית של סגירת מבצעים</h2>
        <button
          onClick={handleRunJob}
          disabled={jobLoading}
          className="px-4 py-2 bg-emerald-500 text-white rounded hover:bg-emerald-600 disabled:bg-gray-400"
        >
          {jobLoading ? <Spinner /> : 'הרץ סגירת מבצעים'}
        </button>
        {jobResult && (
          <div className="mt-4 text-sm bg-slate-50 rounded p-3">
            <p>מבצעים נסגרים: {jobResult.closed_count}</p>
            <p>מבצעים כושלים: {jobResult.failed_count}</p>
          </div>
        )}
      </div>
    </PageContainer>
  );
};