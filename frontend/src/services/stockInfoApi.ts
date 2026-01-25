/**
 * Stock Info API Service
 * Handles API calls to backend for individual stock information
 */

import axios from 'axios';

export interface StockInfoResponse {
  stock_code: string;
  data: Record<string, string>;
  source_status: {
    em_api: 'success' | 'failed';
    xq_api: 'success' | 'failed';
  };
}

export interface StockInfoError {
  error: string;
}

class StockInfoApiService {
  private readonly baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  /**
   * Get individual stock information
   */
  async getStockInfo(stockCode: string): Promise<StockInfoResponse> {
    try {
      const response = await axios.get<StockInfoResponse>(
        `${this.baseUrl}/stocks/${stockCode}/info`,
        {
          timeout: 30000, // 30 second timeout
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // Handle specific HTTP errors
        if (error.response?.status === 400) {
          throw new Error('Invalid stock code format');
        }
        if (error.response?.status === 404) {
          throw new Error('Stock data not available');
        }
        if (error.response?.status === 429) {
          throw new Error('Rate limit exceeded, please try again later');
        }
        if (error.response?.status === 500) {
          throw new Error('Server error, please try again later');
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