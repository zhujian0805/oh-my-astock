"""Frontend API tests for stockService API calls."""

import pytest
from unittest.mock import patch, MagicMock
import axios from 'axios'

// Mock axios for all tests
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('StockService API Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const { fetchStocks, getStockByCode, searchStocks } = require('../../src/services/stockService');

  describe('fetchStocks', () => {
    it('should successfully fetch stocks with default parameters', async () => {
      const mockResponse = {
        data: {
          data: [
            { code: '000001', name: '平安银行' },
            { code: '600036', name: '招商银行' }
          ],
          pagination: {
            total: 5000,
            limit: 50,
            offset: 0,
            has_more: true
          }
        }
      };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const result = await fetchStocks();

      expect(mockedAxios.get).toHaveBeenCalledWith('/stocks', {
        params: { limit: 50, offset: 0 }
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should fetch stocks with custom parameters', async () => {
      const mockResponse = {
        data: {
          data: [{ code: '000001', name: '平安银行' }],
          pagination: {
            total: 5000,
            limit: 10,
            offset: 20,
            has_more: true
          }
        }
      };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const result = await fetchStocks(10, 20);

      expect(mockedAxios.get).toHaveBeenCalledWith('/stocks', {
        params: { limit: 10, offset: 20 }
      });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('getStockByCode', () => {
    it('should successfully fetch individual stock', async () => {
      const stockCode = '000001';
      const mockStock = { code: '000001', name: '平安银行' };
      const mockResponse = { data: mockStock };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const result = await getStockByCode(stockCode);

      expect(mockedAxios.get).toHaveBeenCalledWith(`/stocks/${stockCode}`);
      expect(result).toEqual(mockStock);
    });
  });

  describe('searchStocks', () => {
    it('should successfully search stocks', async () => {
      const query = '平安';
      const mockStocks = [
        { code: '000001', name: '平安银行' }
      ];
      const mockResponse = { data: { data: mockStocks } };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const result = await searchStocks(query);

      expect(mockedAxios.get).toHaveBeenCalledWith('/stocks/search', {
        params: { q: query, limit: 20 }
      });
      expect(result).toEqual(mockStocks);
    });

    it('should search stocks with custom limit', async () => {
      const query = '招商';
      const limit = 50;
      const mockStocks = [
        { code: '600036', name: '招商银行' }
      ];
      const mockResponse = { data: { data: mockStocks } };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const result = await searchStocks(query, limit);

      expect(mockedAxios.get).toHaveBeenCalledWith('/stocks/search', {
        params: { q: query, limit }
      });
      expect(result).toEqual(mockStocks);
    });
  });
});</content>
<parameter name="file_path">tests/integration/test_stock_service_apis.test.js