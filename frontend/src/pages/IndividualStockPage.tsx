/**
 * Individual Stock Page
 * Page for viewing individual stock information with dropdown selection
 */

import React, { useState, useCallback } from 'react';
import StockInfoDropdown from '../components/StockInfoDropdown';
import StockInfoDisplay from '../components/StockInfoDisplay';
import { stockInfoApi, StockInfoResponse } from '../services/stockInfoApi';

const IndividualStockPage: React.FC = () => {
  const [selectedStock, setSelectedStock] = useState<string>('');
  const [stockData, setStockData] = useState<StockInfoResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleStockChange = useCallback(async (stockCode: string) => {
    setSelectedStock(stockCode);
    setError(null);

    if (!stockCode) {
      setStockData(null);
      return;
    }

    // Validate stock code
    if (!stockInfoApi.isValidStockCode(stockCode)) {
      setError('股票代码格式无效，请输入6位数字');
      setStockData(null);
      return;
    }

    setLoading(true);
    try {
      const data = await stockInfoApi.getStockInfo(stockCode);
      setStockData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取股票信息失败');
      setStockData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            个股信息
          </h1>
          <p className="text-gray-600">
            选择股票代码查看详细的个股信息，包括来自东方财富和雪球的数据
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <StockInfoDropdown
            value={selectedStock}
            onChange={handleStockChange}
            disabled={loading}
            className="max-w-md"
          />
        </div>

        {stockData && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                股票代码: {stockData.stock_code}
              </h2>
            </div>
            <StockInfoDisplay
              data={stockData.data}
              sourceStatus={stockData.source_status}
              loading={loading}
              error={error}
            />
          </div>
        )}

        {!stockData && !loading && !error && selectedStock && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <p className="text-gray-500 text-center">
              选择股票代码开始查看信息
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default IndividualStockPage;