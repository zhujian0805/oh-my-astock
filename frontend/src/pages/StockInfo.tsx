import React, { useState, useEffect } from 'react';
import StockSelector from '../components/StockSelector/StockSelector';
import StockInfoDisplay from '../components/StockInfoDisplay';
import { stockInfoApi } from '../services/stockInfoApi';
import { StockListItem } from '../types';

const StockInfo: React.FC = () => {
  const [selectedStock, setSelectedStock] = useState<StockListItem | null>(null);
  const [stocks, setStocks] = useState<StockListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStockList();
  }, []);

  const fetchStockList = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await stockInfoApi.getStockList();
      setStocks(response.stocks);
    } catch (err: any) {
      setError(err.message || '获取股票列表失败');
      console.error('Error fetching stock list:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStockSelect = (stock: StockListItem) => {
    setSelectedStock(stock);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        个股信息
      </h1>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            选择股票
          </label>
          <StockSelector
            stocks={stocks}
            selectedStock={selectedStock}
            onSelect={handleStockSelect}
            isLoading={isLoading}
            error={error}
          />
        </div>

        {selectedStock && (
          <div className="text-sm text-gray-600 dark:text-gray-400">
            已选择股票: <span className="font-mono font-medium">{selectedStock.code} - {selectedStock.name}</span>
          </div>
        )}
      </div>

      {selectedStock && (
        <StockInfoDisplay stockCode={selectedStock.code} />
      )}
    </div>
  );
};

export default StockInfo;