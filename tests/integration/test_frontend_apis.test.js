"""Frontend API integration tests for all API service calls."""

import pytest
from unittest.mock import patch, MagicMock
import axios from 'axios'

// Mock axios for all tests
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Frontend API Services Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('StockInfoApiService', () => {
    const { stockInfoApi } = require('../../src/services/stockInfoApi');

    describe('getStockList', () => {
      it('should successfully fetch stock list', async () => {
        const mockResponse = {
          data: {
            stocks: [
              { code: '000001', name: '平安银行', exchange: 'Shenzhen' },
              { code: '600036', name: '招商银行', exchange: 'Shanghai' }
            ]
          }
        };
        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        const result = await stockInfoApi.getStockList();

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/stocks', {
          timeout: 10000
        });
        expect(result).toEqual(mockResponse.data);
      });

      it('should handle API errors', async () => {
        const errorMessage = 'Failed to fetch stock list';
        mockedAxios.get.mockRejectedValueOnce({
          isAxiosError: true,
          response: { data: { error: errorMessage } }
        });

        await expect(stockInfoApi.getStockList()).rejects.toThrow(errorMessage);
      });

      it('should handle network errors', async () => {
        mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

        await expect(stockInfoApi.getStockList()).rejects.toThrow('Network error, please check your connection');
      });
    });

    describe('getStockInfo', () => {
      it('should successfully fetch individual stock info', async () => {
        const stockCode = '000001';
        const mockResponse = {
          data: {
            code: '000001',
            name: '平安银行',
            current_price: 10.5,
            data_sources: { east_money: true },
            last_updated: '2024-01-01T00:00:00Z'
          }
        };
        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        const result = await stockInfoApi.getStockInfo(stockCode);

        expect(mockedAxios.get).toHaveBeenCalledWith(`/api/v1/stocks/${stockCode}`, {
          timeout: 30000
        });
        expect(result).toEqual(mockResponse.data);
      });

      it('should handle 400 errors', async () => {
        mockedAxios.get.mockRejectedValueOnce({
          isAxiosError: true,
          response: { status: 400, data: { error: 'Invalid stock code' } }
        });

        await expect(stockInfoApi.getStockInfo('invalid')).rejects.toThrow('Invalid stock code format');
      });

      it('should handle 404 errors', async () => {
        mockedAxios.get.mockRejectedValueOnce({
          isAxiosError: true,
          response: { status: 404, data: { error: 'Stock not found' } }
        });

        await expect(stockInfoApi.getStockInfo('999999')).rejects.toThrow('Stock data not available');
      });

      it('should handle 429 errors', async () => {
        mockedAxios.get.mockRejectedValueOnce({
          isAxiosError: true,
          response: { status: 429 }
        });

        await expect(stockInfoApi.getStockInfo('000001')).rejects.toThrow('Rate limit exceeded, please try again later');
      });

      it('should handle 500 errors', async () => {
        mockedAxios.get.mockRejectedValueOnce({
          isAxiosError: true,
          response: { status: 500, data: { error: 'Server error' } }
        });

        await expect(stockInfoApi.getStockInfo('000001')).rejects.toThrow('Server error, please try again later');
      });
    });

    describe('isValidStockCode', () => {
      it('should validate correct stock codes', () => {
        expect(stockInfoApi.isValidStockCode('000001')).toBe(true);
        expect(stockInfoApi.isValidStockCode('600036')).toBe(true);
        expect(stockInfoApi.isValidStockCode('300750')).toBe(true);
      });

      it('should reject invalid stock codes', () => {
        expect(stockInfoApi.isValidStockCode('123')).toBe(false);
        expect(stockInfoApi.isValidStockCode('1234567')).toBe(false);
        expect(stockInfoApi.isValidStockCode('abc123')).toBe(false);
        expect(stockInfoApi.isValidStockCode('')).toBe(false);
      });
    });
  });

  describe('MarketQuotesApiService', () => {
    const { marketQuotesApi } = require('../../src/services/marketQuotesApi');

    describe('getMarketQuotes', () => {
      it('should successfully fetch market quotes without parameters', async () => {
        const mockResponse = {
          data: {
            quotes: [
              {
                stock_code: '000001',
                latest_price: 10.5,
                last_updated: '2024-01-01T00:00:00Z'
              }
            ],
            metadata: {
              total_quotes: 1,
              last_updated: '2024-01-01T00:00:00Z',
              data_source: 'test'
            }
          }
        };
        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        const result = await marketQuotesApi.getMarketQuotes();

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/market-quotes', {
          params: {},
          timeout: 30000
        });
        expect(result).toEqual(mockResponse.data);
      });

      it('should fetch market quotes with stock parameters', async () => {
        const stocks = '000001,600036';
        const mockResponse = {
          data: {
            quotes: [],
            metadata: {
              total_quotes: 0,
              last_updated: '2024-01-01T00:00:00Z',
              data_source: 'test'
            }
          }
        };
        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        const result = await marketQuotesApi.getMarketQuotes(stocks);

        expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/market-quotes', {
          params: { stocks },
          timeout: 30000
        });
        expect(result).toEqual(mockResponse.data);
      });

      it('should handle API errors', async () => {
        mockedAxios.get.mockRejectedValueOnce({
          isAxiosError: true,
          response: { status: 500 }
        });

        await expect(marketQuotesApi.getMarketQuotes()).rejects.toThrow('Server error, please try again later');
      });
    });

    describe('validateStockCodes', () => {
      it('should validate correct stock code lists', () => {
        expect(marketQuotesApi.validateStockCodes('000001,600036,300750')).toBe(true);
        expect(marketQuotesApi.validateStockCodes('000001')).toBe(true);
      });

      it('should accept empty stock codes', () => {
        expect(marketQuotesApi.validateStockCodes('')).toBe(true);
        expect(marketQuotesApi.validateStockCodes('   ')).toBe(true);
      });

      it('should reject invalid stock codes', () => {
        expect(marketQuotesApi.validateStockCodes('000001,invalid,600036')).toBe(false);
        expect(marketQuotesApi.validateStockCodes('123')).toBe(false);
      });
    });
  });
});</content>
<parameter name="file_path">tests/integration/test_frontend_apis.test.js