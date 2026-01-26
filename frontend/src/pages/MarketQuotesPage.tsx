import React, { useState, useEffect } from 'react';
import MarketQuotesTable from '../components/MarketQuotesTable';

const MarketQuotesPage: React.FC = () => {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        行情报价
      </h1>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="mb-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            当前市场行情
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            显示股票的实时买卖盘价格和交易信息
          </p>
        </div>

        <MarketQuotesTable />
      </div>
    </div>
  );
};

export default MarketQuotesPage;