import axios from 'axios';
import { API_BASE_URL } from '../lib/env';

export const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});