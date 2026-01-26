/**
 * Market Quotes API Service
 * Handles API calls to backend for market quotes data
 */

import axios from 'axios';

export interface MarketQuote {
  stock_code: string;
  stock_name?: string;
  bid_price_1?: number;
  bid_volume_1?: number;
  bid_price_2?: number;
  bid_volume_2?: number;
  bid_price_3?: number;
  bid_volume_3?: number;
  bid_price_4?: number;
  bid_volume_4?: number;
  bid_price_5?: number;
  bid_volume_5?: number;
  ask_price_1?: number;
  ask_volume_1?: number;
  ask_price_2?: number;
  ask_volume_2?: number;
  ask_price_3?: number;
  ask_volume_3?: number;
  ask_price_4?: number;
  ask_volume_4?: number;
  ask_price_5?: number;
  ask_volume_5?: number;
  latest_price?: number;
  average_price?: number;
  change_amount?: number;
  change_percent?: number;
  volume?: number;
  turnover?: number;
  turnover_rate?: number;
  volume_ratio?: number;
  high?: number;
  low?: number;
  open?: number;
  previous_close?: number;
  limit_up?: number;
  limit_down?: number;
  external_volume?: number;
  internal_volume?: number;
  last_updated: string;
  data_source: string;
  error?: string;
}

export interface MarketQuotesResponse {
  quotes: MarketQuote[];
  metadata: {
    total_quotes: number;
    last_updated: string;
    data_source: string;
  };
}

export interface MarketQuotesError {
  error: string;
  message?: string;
}

class MarketQuotesApiService {
  private readonly baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  /**
   * Get market quotes for stocks
   */
  async getMarketQuotes(stocks?: string): Promise<MarketQuotesResponse> {
    try {
      const params = stocks ? { stocks } : {};
      const response = await axios.get<MarketQuotesResponse>(
        `${this.baseUrl}/market-quotes`,
        {
          params,
          timeout: 30000, // 30 second timeout
        }
      );

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // Handle specific HTTP errors
        if (error.response?.status === 400) {
          throw new Error('Invalid stock codes format');
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
   * Validate stock codes format
   */
  validateStockCodes(stocks: string): boolean {
    if (!stocks || !stocks.trim()) return true; // Empty is valid (use defaults)

    const codes = stocks.split(',').map(code => code.trim());
    return codes.every(code => /^\d{6}$/.test(code));
  }
}

// Export singleton instance
export const marketQuotesApi = new MarketQuotesApiService();
export default marketQuotesApi;