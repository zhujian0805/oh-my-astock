/**
 * Custom useFetch Hook
 * Handles data fetching with caching, loading states, and error handling
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import apiClient from '../services/api';
import { ApiError, FetchState } from '../types';

/**
 * Cache store for fetch results
 */
interface CacheEntry<T> {
  data: T;
  expiry: number;
}

const cacheStore = new Map<string, CacheEntry<any>>();

/**
 * Custom hook for fetching data with caching
 * @param url - The API endpoint URL
 * @param options - Configuration options
 * @returns FetchState with data, loading, error, and refetch function
 */
export function useFetch<T>(
  url: string,
  options?: { skip?: boolean; ttl?: number }
): FetchState<T> {
  const skipRef = useRef(options?.skip);
  skipRef.current = options?.skip;

  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: ApiError | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const cacheRef = useRef(options?.ttl || 5 * 60 * 1000); // 5 minute default TTL

  /**
   * Fetch data from API or cache
   */
  const fetchData = useCallback(async () => {
    // Check cache first
    const cached = cacheStore.get(url);
    if (cached && Date.now() < cached.expiry) {
      setState({ data: cached.data, loading: false, error: null });
      return;
    }

    setState((prev) => ({ ...prev, loading: true }));

    try {
      const response = await apiClient.get<T>(url);
      const data = response.data;

      // Store in cache
      cacheStore.set(url, {
        data,
        expiry: Date.now() + cacheRef.current,
      });

      setState({ data, loading: false, error: null });
    } catch (error: any) {
      const apiError = error as ApiError;
      setState({ data: null, loading: false, error: apiError });
    }
  }, [url]);

  /**
   * Effect to fetch data when URL changes
   */
  useEffect(() => {
    let ignore = false;

    if (skipRef.current) {
      setState({ data: null, loading: false, error: null });
      return;
    }

    // Check cache immediately to prevent flash of loading if data exists
    const cached = cacheStore.get(url);
    if (cached && Date.now() < cached.expiry) {
      // Let the async fetchData handle the state update to be consistent
      // But we could optimistically set it here if we wanted
    } else {
      // Clear previous data and set loading state for new request
      setState({ data: null, loading: true, error: null });
    }

    (async () => {
      await fetchData();
      // Prevent state update if component unmounted
      if (!ignore) {
        // State already updated in fetchData
      }
    })();

    return () => {
      ignore = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  /**
   * Refetch data, bypassing cache
   */
  const refetch = useCallback(() => {
    cacheStore.delete(url);
    setState({ data: null, loading: true, error: null });
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  return {
    ...state,
    refetch,
  };
}

/**
 * Clear all cached data
 */
export function clearCache(): void {
  cacheStore.clear();
}

/**
 * Clear specific cache entry
 */
export function clearCacheEntry(url: string): void {
  cacheStore.delete(url);
}

export default useFetch;
