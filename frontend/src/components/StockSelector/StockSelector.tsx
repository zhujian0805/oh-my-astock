/**
 * StockSelector Component
 * Dropdown to select stocks from the list
 */

import React, { useState, useMemo } from 'react';
import { Stock, StockSelectorProps } from '../../types';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import EmptyState from '../common/EmptyState';

const StockSelector: React.FC<StockSelectorProps> = ({
  stocks,
  selectedStock,
  onSelect,
  isLoading = false,
  error = null,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Filter stocks based on search query
  const filteredStocks = useMemo(() => {
    if (!searchQuery.trim()) {
      return stocks;
    }

    const q = searchQuery.toLowerCase();
    return stocks.filter(
      (stock) =>
        stock.code.toLowerCase().includes(q) ||
        stock.name.toLowerCase().includes(q)
    );
  }, [stocks, searchQuery]);

  const handleSelect = (stock: Stock) => {
    onSelect(stock);
    setIsOpen(false);
    setSearchQuery('');
  };

  if (error) {
    return <ErrorMessage error={error} onRetry={() => {}} />;
  }

  if (isLoading && stocks.length === 0) {
    return <LoadingSpinner message="加载股票中..." />;
  }

  if (stocks.length === 0) {
    return (
      <EmptyState
        title="无可用股票"
        description="请初始化数据库中的股票数据"
      />
    );
  }

  return (
    <div className="">
      <div className="relative">
        {/* Stock Selector Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full px-3 py-1.5 text-left bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg focus:outline-none transition-colors group"
        >
          <div className="flex justify-between items-center">
            <div>
              <p className="text-[10px] text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide">已选股票</p>
              <p className="text-sm font-normal text-gray-900 dark:text-white mt-0">
                {selectedStock ? `${selectedStock.code} - ${selectedStock.name}` : '选择股票'}
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
                  placeholder="按代码或名称搜索..."
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
                    <p>未找到股票</p>
                  </div>
                ) : (
                  filteredStocks.map((stock) => (
                    <button
                      key={stock.code}
                      onClick={() => handleSelect(stock)}
                      className={`w-full px-4 py-3 text-left rounded-md transition-colors ${
                        selectedStock?.code === stock.code 
                          ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400' 
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-sm">{stock.code}</p>
                          <p className="text-xs opacity-80">{stock.name}</p>
                        </div>
                        {selectedStock?.code === stock.code && (
                          <svg
                            className="w-5 h-5 text-primary-600 dark:text-primary-400"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
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

export default React.memo(StockSelector);
