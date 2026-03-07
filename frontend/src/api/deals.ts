import { client } from './client';
import { z } from 'zod';

export const DealSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  status: z.enum(['ACTIVE', 'CLOSED', 'FAILED']),
  current_qty: z.number(),
  min_qty_to_close: z.number(),
  price_cents: z.number(),
  end_at: z.string(),
  description: z.string().optional(),
  image_url: z.string().optional(),
});

export type Deal = z.infer<typeof DealSchema>;

export const JoinPayloadSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email address'),
  qty: z.number().int().min(1, 'Qty must be at least 1'),
});

export type JoinPayload = z.infer<typeof JoinPayloadSchema>;

export const listDeals = async (): Promise<Deal[]> => {
  const response = await client.get('/deals');
  return response.data.data.items;
};

export const getDeal = async (dealId: string): Promise<Deal> => {
  const response = await client.get(`/deals/${dealId}`);
  return response.data.data;
};

export const joinDeal = async (dealId: string, payload: JoinPayload): Promise<Deal> => {
  // FastAPI expects the join parameters as query values, not a JSON body.
  // axios supports this via the `params` option; the body is null.
  const response = await client.post(
    `/deals/${dealId}/join`,
    null,
    { params: payload }
  );
  return response.data.data.deal;
};