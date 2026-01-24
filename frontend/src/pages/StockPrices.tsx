/**
 * StockPrices Page Component
 * Main page for viewing stock price history
 * Integrates StockSelector and StockChart
 */

import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import { Stock } from '@/types';
import StockSelector from '@/components/StockSelector/StockSelector';
import StockChart from '@/components/StockChart/StockChart';
import StockTable from '@/components/StockTable/StockTable';
import { useStocks } from '@/hooks/useStocks';
import { useHistoricalData } from '@/hooks/useHistoricalData';
import { formatDate } from '@/utils/formatters';

const StockPrices: React.FC = () => {
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

  // Fetch stocks list
  const { stocks, isLoading: stocksLoading, error: stocksError } = useStocks();

  // Fetch historical data for selected stock
  const {
    chartData,
    prices,
    isLoading: chartLoading,
    error: chartError,
  } = useHistoricalData(
    selectedStock?.code || null,
    startDate ? formatDate(startDate) : undefined,
    endDate ? formatDate(endDate) : undefined
  );

  // Log date selection changes
  React.useEffect(() => {
    if (selectedStock) {
      console.log('[StockPrices] Date selection changed:', {
        stock: selectedStock.code,
        startDate: startDate ? formatDate(startDate) : null,
        endDate: endDate ? formatDate(endDate) : null,
        chartDataPoints: chartData?.dates?.length || 0,
        isLoading: chartLoading
      });
    }
  }, [startDate, endDate, selectedStock, chartData, chartLoading]);

  return (
    <div className="flex flex-col h-full gap-2 w-full p-1 dark:bg-gray-900 transition-colors duration-200">
      {/* Controls Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 p-2 flex flex-col md:flex-row gap-2 items-center justify-between transition-colors duration-200">
        <div className="w-full md:w-96">
          <StockSelector
            stocks={stocks}
            selectedStock={selectedStock}
            onSelect={setSelectedStock}
            isLoading={stocksLoading}
            error={stocksError}
          />
        </div>
        
        <div className="flex items-center gap-2 w-full md:w-auto">
          <div className="flex flex-col z-20 relative">
             <label className="text-[10px] text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide mb-0.5">开始日期</label>
             <DatePicker
               selected={startDate}
               onChange={(date) => setStartDate(date)}
               dateFormat="yyyy-MM-dd"
               className="w-full px-2 py-1.5 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-primary-500"
               placeholderText="开始日期"
             />
          </div>
          <div className="flex flex-col z-20 relative">
             <label className="text-[10px] text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide mb-0.5">结束日期</label>
             <DatePicker
               selected={endDate}
               onChange={(date) => setEndDate(date)}
               dateFormat="yyyy-MM-dd"
               className="w-full px-2 py-1.5 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-primary-500"
               placeholderText="结束日期"
             />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col gap-2 min-h-0">
        {selectedStock ? (
          <>
            {/* Chart Section */}
            <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden min-h-[300px] transition-colors duration-200">
              <StockChart
                chartData={chartData}
                stockCode={selectedStock.code}
                isLoading={chartLoading}
                error={chartError}
              />
            </div>

            {/* Table Section */}
            <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden min-h-[200px] flex flex-col transition-colors duration-200">
              <StockTable data={prices} />
            </div>
          </>
        ) : (
          <div className="flex-1 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 flex items-center justify-center transition-colors duration-200">
            <div className="text-center">
              <div className="mx-auto h-16 w-16 bg-gray-50 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
                <svg
                  className="h-8 w-8 text-gray-400 dark:text-gray-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-normal text-gray-900 dark:text-white">
                选择股票
              </h3>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                选择股票和日期范围查看价格历史
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StockPrices;
