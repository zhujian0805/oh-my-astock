/**
 * Stock Service
 * Handles all stock-related API calls
 */

import apiClient from './api';
import { Stock, StockListResponse } from '../types';

/**
 * Fetch all stocks with pagination
 */
export async function fetchStocks(limit: number = 50, offset: number = 0): Promise<StockListResponse> {
  const response = await apiClient.get<StockListResponse>('/stocks', {
    params: { limit, offset },
  });
  return response.data;
}

/**
 * Get a single stock by code
 */
export async function getStockByCode(code: string): Promise<Stock> {
  const response = await apiClient.get<Stock>(`/stocks/${code}`);
  return response.data;
}

/**
 * Search stocks by name or code
 */
export async function searchStocks(query: string, limit: number = 20): Promise<Stock[]> {
  const response = await apiClient.get<{ data: Stock[] }>('/stocks/search', {
    params: { q: query, limit },
  });
  return response.data.data;
}

export default {
  fetchStocks,
  getStockByCode,
  searchStocks,
};
