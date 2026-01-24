/**
 * StockTable Component
 * Displays historical price data in a tabular format
 */

import React from 'react';
import { HistoricalPrice } from '../../types';

interface StockTableProps {
  data: HistoricalPrice[];
}

const StockTable: React.FC<StockTableProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return null;
  }

  return (
    <div className="flex-1 min-h-0 overflow-hidden flex flex-col bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 transition-colors duration-200">
      <div className="overflow-auto flex-1">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700 sticky top-0 z-10">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                日期
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                开盘
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                最高
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                最低
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                收盘
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                成交量
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                涨跌
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {data.map((row, index) => {
              const prevClose = index < data.length - 1 ? data[index + 1].close_price : row.open_price;
              const change = row.close_price - prevClose;
              const changePercent = (change / prevClose) * 100;
              const isPositive = change >= 0;

              return (
                <tr key={row.date} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100 font-medium">
                    {row.date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right">
                    {row.open_price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right">
                    {row.high_price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right">
                    {row.low_price.toFixed(2)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium text-right ${isPositive ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
                    {row.close_price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right">
                    {row.volume.toLocaleString()}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm text-right ${isPositive ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
                    {change > 0 ? '+' : ''}{change.toFixed(2)} ({change > 0 ? '+' : ''}{changePercent.toFixed(2)}%)
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default React.memo(StockTable);
