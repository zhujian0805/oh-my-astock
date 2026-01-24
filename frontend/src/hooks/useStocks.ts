/**
 * useStocks Hook
 * Manages stock list fetching and caching
 */

import { useMemo } from 'react';
import { fetchStocks } from '../services/stockService';
import { Stock, UseStocksReturn, StockListResponse } from '../types';
import { useFetch } from './useFetch';

/**
 * Custom hook to fetch and manage stock list
 * Caches results for 10 minutes by default
 */
export function useStocks(limit: number = 10000, offset: number = 0): UseStocksReturn {
  // Fetch all stocks with pagination
  const { data: response, loading, error, refetch } = useFetch<StockListResponse>(
    `/stocks?limit=${limit}&offset=${offset}`,
    { ttl: 10 * 60 * 1000 } // 10 minute cache
  );

  // Extract and flatten stock data
  const stocks: Stock[] = useMemo(() => {
    if (!response || !response.data || !Array.isArray(response.data)) {
      return [];
    }
    return response.data;
  }, [response]);

  // Filter stocks by name or code
  const searchStocks = (query: string): Stock[] => {
    if (!query.trim()) {
      return stocks;
    }

    const q = query.toLowerCase();
    return stocks.filter(
      (stock) =>
        stock.code.toLowerCase().includes(q) ||
        stock.name.toLowerCase().includes(q)
    );
  };

  return {
    stocks,
    isLoading: loading,
    data: stocks,
    loading,
    error,
    refetch,
  };
}

export function useStocksSearch(query: string, limit: number = 10000) {
  const { stocks, isLoading, error, refetch } = useStocks(limit);

  const filteredStocks = useMemo(() => {
    if (!query.trim()) {
      return stocks;
    }

    const q = query.toLowerCase();
    return stocks.filter(
      (stock) =>
        stock.code.toLowerCase().includes(q) ||
        stock.name.toLowerCase().includes(q)
    );
  }, [stocks, query]);

  return {
    stocks: filteredStocks,
    isLoading,
    error,
    refetch,
  };
}

export default useStocks;
