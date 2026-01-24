/**
 * useHistoricalData Hook
 * Manages historical price data fetching and transformation
 */

import { useMemo } from 'react';
import { useFetch } from './useFetch';
import { HistoricalPrice, UseHistoricalDataReturn, ChartData } from '../types';
import { transformPriceData } from '../utils/charts';

/**
 * Custom hook to fetch and manage historical price data
 */
export function useHistoricalData(
  stockCode: string | null,
  startDate?: string,
  endDate?: string
): UseHistoricalDataReturn {
  // Build API URL with optional date parameters
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const queryString = params.toString();
  const url = stockCode ? `/stocks/${stockCode}/historical${queryString ? '?' + queryString : ''}` : '';

  // Fetch data (skips fetch if no stockCode)
  const { data: response, loading, error, refetch } = useFetch(url, {
    skip: !stockCode,
    ttl: 30 * 60 * 1000, // 30 minute cache for historical data
  });

  // Extract and validate price data
  const prices = useMemo(() => {
    if (!response || !Array.isArray((response as any).data)) {
      return [];
    }

    const data = (response as any).data as HistoricalPrice[];

    // Validate and filter (remove invalid records only)
    const validData = data.filter(
      (item) => item.date && !isNaN(item.close_price) && item.close_price > 0
    );

    // No client-side date filtering needed since backend handles it
    return validData;
  }, [response]);

  // Transform to chart data
  const chartData = useMemo(() => {
    if (prices.length === 0) {
      return null;
    }
    return transformPriceData(prices);
  }, [prices]);

  return {
    prices,
    chartData,
    isLoading: loading,
    data: prices,
    loading,
    error,
    refetch,
  };
}

export default useHistoricalData;
