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
  const [formData, setFormData] = useState({ name: '', email: '', qty: 1 });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { showToast } = useToast();
  const queryClient = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: () => joinDeal(dealId, formData),
    onSuccess: () => {
      showToast('Joined successfully!', 'success');
      queryClient.invalidateQueries({ queryKey: ['deal', dealId] });
      queryClient.invalidateQueries({ queryKey: ['deals'] });
      setFormData({ name: '', email: '', qty: 1 });
      setErrors({});
    },
    onError: (error) => {
      showToast((error as any).response?.data?.detail || 'Failed to join deal', 'error');
    },
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
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
    return <p className="text-gray-500">This deal is not active</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow">
      <h2 className="text-lg font-bold mb-4">Join this Deal</h2>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Name</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className="w-full border rounded px-3 py-2"
          disabled={isPending}
        />
        {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className="w-full border rounded px-3 py-2"
          disabled={isPending}
        />
        {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Quantity</label>
        <input
          type="number"
          name="qty"
          value={formData.qty}
          onChange={handleChange}
          min="1"
          className="w-full border rounded px-3 py-2"
          disabled={isPending}
        />
        {errors.qty && <p className="text-red-500 text-xs mt-1">{errors.qty}</p>}
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="w-full bg-blue-500 text-white py-2 rounded font-medium hover:bg-blue-600 disabled:bg-gray-400"
      >
        {isPending ? <Spinner /> : 'Join Deal'}
      </button>
    </form>
  );
};