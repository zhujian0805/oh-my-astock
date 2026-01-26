/**
 * MultiStockSelector Component
 * Dropdown to select multiple stocks for watchlist
 */

import React, { useState, useMemo, useEffect } from 'react';
import { StockListItem } from '../types';

interface MultiStockSelectorProps {
  stocks: StockListItem[];
  selectedStocks: string[];
  onSelectionChange: (stockCodes: string[]) => void;
  isLoading?: boolean;
  error?: string | null;
}

const MultiStockSelector: React.FC<MultiStockSelectorProps> = ({
  stocks,
  selectedStocks,
  onSelectionChange,
  isLoading = false,
  error = null,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Get selected stock objects for display
  const selectedStockObjects = useMemo(() => {
    return stocks.filter(stock => selectedStocks.includes(stock.code));
  }, [stocks, selectedStocks]);

  // Filter available stocks (exclude already selected)
  const availableStocks = useMemo(() => {
    const selectedSet = new Set(selectedStocks);
    return stocks.filter(stock => !selectedSet.has(stock.code));
  }, [stocks, selectedStocks]);

  // Filter available stocks based on search query
  const filteredStocks = useMemo(() => {
    if (!searchQuery.trim()) {
      return availableStocks;
    }

    const q = searchQuery.toLowerCase();
    return availableStocks.filter(
      (stock) =>
        stock.code.toLowerCase().includes(q) ||
        stock.name.toLowerCase().includes(q)
    );
  }, [availableStocks, searchQuery]);

  const handleAddStock = (stock: StockListItem) => {
    const newSelection = [...selectedStocks, stock.code];
    onSelectionChange(newSelection);
    setSearchQuery('');
  };

  const handleRemoveStock = (stockCode: string) => {
    const newSelection = selectedStocks.filter(code => code !== stockCode);
    onSelectionChange(newSelection);
  };

  const handleClearAll = () => {
    onSelectionChange([]);
  };

  if (error) {
    return (
      <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
        <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
      </div>
    );
  }

  if (isLoading && stocks.length === 0) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">加载股票中...</span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Selected Stocks Display */}
      {selectedStocks.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              已选股票 ({selectedStocks.length})
            </label>
            <button
              onClick={handleClearAll}
              className="text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
            >
              清空全部
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedStockObjects.map((stock) => (
              <div
                key={stock.code}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
              >
                <span>{stock.code}</span>
                <button
                  onClick={() => handleRemoveStock(stock.code)}
                  className="ml-1 hover:bg-blue-200 dark:hover:bg-blue-800/50 rounded-full p-0.5"
                >
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stock Selector Dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full px-3 py-2 text-left bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg focus:outline-none transition-colors group border border-gray-200 dark:border-gray-600"
        >
          <div className="flex justify-between items-center">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">添加股票到关注列表</p>
              <p className="text-sm text-gray-900 dark:text-white">
                点击搜索并添加股票...
              </p>
            </div>
            <div className="bg-white dark:bg-gray-600 p-1 rounded-full shadow-sm text-gray-500 dark:text-gray-300 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              <svg
                className={`w-4 h-4 transition-transform ${
                  isOpen ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
          </div>
        </button>

        {/* Dropdown Menu */}
        {isOpen && (
          <>
            {/* Overlay */}
            <div
              className="fixed inset-0 z-30"
              onClick={() => setIsOpen(false)}
            />

            {/* Dropdown List */}
            <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-100 dark:border-gray-700 z-40 max-h-96 overflow-hidden flex flex-col">
              {/* Search Input */}
              <div className="p-3 border-b border-gray-100 dark:border-gray-700 flex-shrink-0">
                <input
                  type="text"
                  placeholder="按代码或名称搜索股票..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border-none rounded-md focus:ring-2 focus:ring-primary-500 text-sm text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  autoFocus
                />
              </div>

              {/* Stock List */}
              <div className="overflow-y-auto flex-1 p-1">
                {filteredStocks.length === 0 ? (
                  <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                    <p className="text-sm">
                      {availableStocks.length === 0
                        ? '所有股票都已添加到关注列表'
                        : '未找到匹配的股票'
                      }
                    </p>
                  </div>
                ) : (
                  filteredStocks.map((stock) => (
                    <button
                      key={stock.code}
                      onClick={() => handleAddStock(stock)}
                      className="w-full px-4 py-3 text-left rounded-md transition-colors hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-sm">{stock.code}</p>
                          <p className="text-xs opacity-80">{stock.name}</p>
                        </div>
                        <svg
                          className="w-5 h-5 text-green-600 dark:text-green-400"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                          />
                        </svg>
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default React.memo(MultiStockSelector);