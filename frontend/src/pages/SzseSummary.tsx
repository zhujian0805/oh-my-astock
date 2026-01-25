/**
 * SzseSummary Page Component
 * Displays Shenzhen Stock Exchange security category statistics
 */

import React, { useState, useEffect } from 'react';
import apiClient from '@/services/api';

interface SZSESummaryRaw {
  [key: string]: string | number;
}

const SzseSummary: React.FC = () => {
  const [data, setData] = useState<SZSESummaryRaw[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSZSESummary();
  }, []);

  const fetchSZSESummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/market/szse-summary');
      const rawData = response.data.data || [];
      setData(rawData);

      // Extract column names from first row
      if (rawData.length > 0) {
        setColumns(Object.keys(rawData[0]));
      }
    } catch (err) {
      console.error('Failed to fetch SZSE summary:', err);
      setError('Failed to load market data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatValue = (value: string | number | undefined): string => {
    if (value === undefined || value === null) return '-';
    if (typeof value === 'number') {
      return value.toFixed(2);
    }
    return String(value);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">加载市场数据中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={fetchSZSESummary}
            className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full gap-4 w-full p-4 dark:bg-gray-900 transition-colors duration-200">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 p-4 flex items-center justify-between transition-colors duration-200">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          深圳证券交易所行情总览
        </h1>
        <button
          onClick={fetchSZSESummary}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors font-medium"
        >
          刷新
        </button>
      </div>

      {/* Table */}
      <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden transition-colors duration-200">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                {columns.map((col) => (
                  <th
                    key={col}
                    className="px-6 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {data.length > 0 ? (
                data.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    {columns.map((col) => (
                      <td
                        key={`${index}-${col}`}
                        className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100 whitespace-nowrap"
                      >
                        {formatValue(row[col])}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={columns.length} className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                    暂无数据
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SzseSummary;