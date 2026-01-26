/**
 * Stock Info API Service
 * Handles API calls to backend for individual stock information
 */

import axios from 'axios';
import { StockListItem, StockInfo } from '../types';

export interface StockListResponse {
  stocks: StockListItem[];
}

export interface StockInfoResponse extends StockInfo {}

export interface StockInfoError {
  error: string;
  code?: string;
  details?: string;
}

class StockInfoApiService {
  private readonly baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  /**
   * Get list of available stocks
   */
  async getStockList(): Promise<StockListResponse> {
    try {
      const response = await axios.get<StockListResponse>(
        `${this.baseUrl}/stocks`,
        {
          timeout: 10000, // 10 second timeout
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || 'Failed to fetch stock list');
      }
      throw new Error('Network error, please check your connection');
    }
  }

  /**
   * Get individual stock information
   */
  async getStockInfo(stockCode: string): Promise<StockInfoResponse> {
    try {
      const response = await axios.get<StockInfoResponse>(
        `${this.baseUrl}/stocks/${stockCode}`,
        {
          timeout: 30000, // 30 second timeout
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // Handle specific HTTP errors
        if (error.response?.status === 400) {
          throw new Error(error.response.data?.error || 'Invalid stock code format');
        }
        if (error.response?.status === 404) {
          throw new Error(error.response.data?.error || 'Stock data not available');
        }
        if (error.response?.status === 429) {
          throw new Error('Rate limit exceeded, please try again later');
        }
        if (error.response?.status === 500) {
          throw new Error(error.response.data?.error || 'Server error, please try again later');
        }

        // Network or other axios error
        throw new Error('Network error, please check your connection');
      }

      // Unknown error
      throw new Error('An unexpected error occurred');
    }
  }

  /**
   * Validate stock code format (6 digits)
   */
  isValidStockCode(stockCode: string): boolean {
    return /^\d{6}$/.test(stockCode);
  }
}

// Export singleton instance
export const stockInfoApi = new StockInfoApiService();
export default stockInfoApi;