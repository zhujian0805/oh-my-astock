/**
 * Historical Data Service
 * Handles historical price data API calls
 */

import apiClient from './api';
import { HistoricalPrice, HistoricalPriceResponse } from '../types';
import { formatDate } from '../utils/formatters';

/**
 * Fetch historical price data for a stock
 */
export async function fetchHistoricalData(
  stockCode: string,
  startDate?: string,
  endDate?: string
): Promise<HistoricalPrice[]> {
  const params: Record<string, string> = {};

  if (startDate) {
    params.start_date = startDate;
  }

  if (endDate) {
    params.end_date = endDate;
  }

  const response = await apiClient.get<HistoricalPriceResponse>(
    `/stocks/${stockCode}/historical`,
    { params }
  );

  return response.data.data;
}

/**
 * Fetch historical data for a stock with date range defaults
 * If no dates provided, fetches data for last 1 year
 */
export async function fetchHistoricalDataLastYear(stockCode: string): Promise<HistoricalPrice[]> {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setFullYear(startDate.getFullYear() - 1);

  return fetchHistoricalData(
    stockCode,
    formatDate(startDate),
    formatDate(endDate)
  );
}

/**
 * Validate historical data
 */
export function validateHistoricalData(data: HistoricalPrice[]): boolean {
  if (!Array.isArray(data) || data.length === 0) {
    return false;
  }

  // Check if data has required fields
  return data.every(
    (item) =>
      item.date &&
      !isNaN(item.close_price) &&
      !isNaN(item.open_price) &&
      !isNaN(item.high_price) &&
      !isNaN(item.low_price)
  );
}

export default {
  fetchHistoricalData,
  fetchHistoricalDataLastYear,
  validateHistoricalData,
};
