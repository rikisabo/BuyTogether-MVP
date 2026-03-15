import { client } from './client';
import { z } from 'zod';
import { Deal } from './deals';

export const CreateDealSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
  image_url: z.string().url('Must be a valid URL').optional(),
  price_cents: z
    .union([z.string(), z.number()])
    .transform(val => (typeof val === 'string' ? Number(val) : val))
    .refine(n => !isNaN(n) && n > 0, 'Price must be positive'),
  min_qty_to_close: z.number().int().positive('Target quantity must be positive'),
  end_at: z.string()
    .refine(v => !isNaN(Date.parse(v)), 'Invalid date')
    .refine(v => new Date(v) > new Date(), 'Deadline must be in the future'),
});

export type CreateDealPayload = z.infer<typeof CreateDealSchema>;

export interface CloseJobResult {
  closed_count: number;
  failed_count: number;
}

export const createDeal = async (payload: CreateDealPayload): Promise<Deal> => {
  const response = await client.post('/admin/deals', payload);
  return response.data.data;
};

export const runCloseJob = async (): Promise<CloseJobResult> => {
  const response = await client.post('/jobs/close-deals');
  return response.data.data;
};