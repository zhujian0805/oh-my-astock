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
    return <LoadingSpinner message="Loading stocks..." />;
  }

  if (stocks.length === 0) {
    return (
      <EmptyState
        title="No stocks available"
        description="Please initialize the database with stock data"
      />
    );
  }

  return (
    <div className="p-6">
      <div className="relative">
        {/* Stock Selector Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full px-4 py-3 text-left bg-white border border-gray-300 rounded-lg hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-500">Selected Stock</p>
              <p className="text-lg font-semibold">
                {selectedStock ? `${selectedStock.code} - ${selectedStock.name}` : 'Select a stock'}
              </p>
            </div>
            <svg
              className={`w-5 h-5 text-gray-400 transition-transform ${
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
                d="M19 14l-7 7m0 0l-7-7m7 7V3"
              />
            </svg>
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
            <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-300 rounded-lg shadow-lg z-40 max-h-96 overflow-hidden flex flex-col">
              {/* Search Input */}
              <div className="p-3 border-b border-gray-200 flex-shrink-0">
                <input
                  type="text"
                  placeholder="Search by code or name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                />
              </div>

              {/* Stock List */}
              <div className="overflow-y-auto flex-1">
                {filteredStocks.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <p>No stocks found</p>
                  </div>
                ) : (
                  filteredStocks.map((stock) => (
                    <button
                      key={stock.code}
                      onClick={() => handleSelect(stock)}
                      className={`w-full px-4 py-3 text-left hover:bg-blue-50 border-b border-gray-100 last:border-b-0 transition-colors ${
                        selectedStock?.code === stock.code ? 'bg-blue-100' : ''
                      }`}
                    >
                      <div className="flex justify-between">
                        <div>
                          <p className="font-semibold text-gray-900">{stock.code}</p>
                          <p className="text-sm text-gray-600">{stock.name}</p>
                        </div>
                        {selectedStock?.code === stock.code && (
                          <svg
                            className="w-5 h-5 text-blue-600"
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
