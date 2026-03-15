import { client } from './client';
import { z } from 'zod';

export const DealSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  description: z.string().optional(),
  image_url: z.string().url().optional(),
  status: z.enum(['ACTIVE', 'CLOSED', 'FAILED']),
  current_qty: z.number(),
  min_qty_to_close: z.number(),
  price_cents: z.number(),
  end_at: z.string(),
});

export type Deal = z.infer<typeof DealSchema>;

// extended deal returned by GET /deals/:id
export interface DealDetail extends Deal {
  participants_count?: number;
}

export const JoinPayloadSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
  qty: z.number().int().min(1, 'Qty must be at least 1'),
  city: z.string().min(1, 'City is required'),
  street: z.string().min(1, 'Street is required'),
  house_number: z.string().min(1, 'House number is required'),
  apartment: z.string().optional(),
  phone: z
    .string()
    .optional()
    .refine(val => !val || /^[+0-9\s()-]+$/.test(val), 'Invalid phone number'),
  notes: z.string().optional(),
});

export type JoinPayload = z.infer<typeof JoinPayloadSchema>;

export interface DealsPage {
  items: Deal[];
  page: number;
  page_size: number;
  total: number;
}

export const listDeals = async (
  params?: { status?: string; page?: number; page_size?: number }
): Promise<DealsPage> => {
  const response = await client.get('/deals', { params });
  return response.data.data as DealsPage;
};

export const getDeal = async (dealId: string): Promise<DealDetail> => {
  const response = await client.get(`/deals/${dealId}`);
  return response.data.data as DealDetail;
};

export const joinDeal = async (
  dealId: string,
  payload: JoinPayload
): Promise<Deal> => {
  const response = await client.post(`/deals/${dealId}/join`, payload);
  return response.data.data.deal;
};