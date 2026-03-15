import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { z } from 'zod';
import { joinDeal, JoinPayloadSchema } from '../api/deals';
import { useToast } from './Toast';
import { Spinner } from './Spinner';

interface JoinFormProps {
  dealId: string;
  isActive: boolean;
}

export const JoinForm: React.FC<JoinFormProps> = ({ dealId, isActive }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    qty: 1,
    city: '',
    street: '',
    house_number: '',
    apartment: '',
    phone: '',
    notes: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [successMessage, setSuccessMessage] = useState('');
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: () => joinDeal(dealId, formData),
    onSuccess: () => {
      const message = 'הצטרפות נקלטה! בדוק את המייל לאישור ההשתתפות.';
      showToast(message, 'success');
      setSuccessMessage('נשלח אימייל אישור לעודכן את ההצטרפות. בדוק את המייל שלך.');
      queryClient.invalidateQueries({ queryKey: ['deal', dealId] });
      queryClient.invalidateQueries({ queryKey: ['deals'] });
      setFormData({
        name: '',
        email: '',
        qty: 1,
        city: '',
        street: '',
        house_number: '',
        apartment: '',
        phone: '',
        notes: '',
      });
      setErrors({});
    },
    onError: (error) => {
      const errorMessage =
        (error as any).response?.data?.error?.message ||
        (error as any).response?.data?.detail ||
        'נכשל בהצטרפות. אנא נסה שוב.';
      showToast(errorMessage, 'error');
    },
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'qty' ? parseInt(value) || 0 : value,
    }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      JoinPayloadSchema.parse(formData);
      mutate();
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors: Record<string, string> = {};
        error.errors.forEach(err => {
          if (err.path[0]) {
            newErrors[err.path[0] as string] = err.message;
          }
        });
        setErrors(newErrors);
      }
    }
  };

  if (!isActive) {
    return <p className="text-gray-500">המבצע אינו זמין להצטרפות כרגע</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl shadow-md">
      <h2 className="text-xl font-bold mb-4">הצטרף לביצוע קנייה</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">שם מלא</label>
          <input
            type="text"
            name="name"
            placeholder="דוגמה: דני כהן"
            value={formData.name}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
            disabled={isPending}
          />
          {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">מייל</label>
          <input
            type="email"
            name="email"
            placeholder="דוגמה: dani@example.com"
            value={formData.email}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
            disabled={isPending}
          />
          {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">כמות</label>
          <input
            type="number"
            name="qty"
            min="1"
            placeholder="1"
            value={formData.qty}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
            disabled={isPending}
          />
          {errors.qty && <p className="text-red-500 text-xs mt-1">{errors.qty}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">עיר</label>
          <input
            type="text"
            name="city"
            placeholder="תל אביב"
            value={formData.city}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
            disabled={isPending}
          />
          {errors.city && <p className="text-red-500 text-xs mt-1">{errors.city}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">רחוב</label>
          <input
            type="text"
            name="street"
            placeholder="דיזנגוף"
            value={formData.street}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
            disabled={isPending}
          />
          {errors.street && <p className="text-red-500 text-xs mt-1">{errors.street}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">מספר בית</label>
          <input
            type="text"
            name="house_number"
            placeholder="15"
            value={formData.house_number}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
            disabled={isPending}
          />
          {errors.house_number && <p className="text-red-500 text-xs mt-1">{errors.house_number}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-2">
        <div>
          <label className="block text-sm font-medium mb-1">דירה (אופציונלי)</label>
          <input
            type="text"
            name="apartment"
            placeholder="3"
            value={formData.apartment}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
            disabled={isPending}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">טלפון (אופציונלי)</label>
          <input
            type="tel"
            name="phone"
            placeholder="05X-XXXXXXX"
            value={formData.phone}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
            disabled={isPending}
          />
          {errors.phone && <p className="text-red-500 text-xs mt-1">{errors.phone}</p>}
        </div>
      </div>

      <div className="mt-4">
        <label className="block text-sm font-medium mb-1">הערות (אופציונלי)</label>
        <textarea
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          placeholder="לדוגמה: דרוש משלוח לדירה קומה 4 ללא מעלית"
          className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-indigo-300"
          disabled={isPending}
        />
      </div>

      {successMessage && (
        <div className="mb-3 rounded-xl bg-emerald-50 border border-emerald-100 p-3 text-emerald-700">
          {successMessage}
        </div>
      )}

      <button
        type="submit"
        disabled={isPending}
        className="w-full bg-indigo-600 text-white py-2 rounded font-semibold hover:bg-indigo-700 disabled:bg-slate-300"
      >
        {isPending ? <Spinner /> : 'הצטרפות להצעה'}
      </button>
      {isPending && <p className="mt-2 text-sm text-slate-500">טוען, נא להמתין...</p>}
    </form>
  );
};