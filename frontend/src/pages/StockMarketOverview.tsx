/**
 * StockMarketOverview Page Component
 * Displays Shanghai Stock Exchange market summary data
 */

import React, { useState, useEffect } from 'react';
import './StockMarketOverview.css';
import apiClient from '@/services/api';

interface SSESummaryRaw {
  [key: string]: string | number;
}

const StockMarketOverview: React.FC = () => {
  const [data, setData] = useState<SSESummaryRaw[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSSESummary();
  }, []);

  const fetchSSESummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get('/market/sse-summary');
      const rawData = response.data.data || [];
      setData(rawData);
      
      // Extract column names from first row
      if (rawData.length > 0) {
        setColumns(Object.keys(rawData[0]));
      }
    } catch (err) {
      console.error('Failed to fetch SSE summary:', err);
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
          <p className="text-gray-600">加载市场数据中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchSSESummary}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            重新加载
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="stock-market-overview p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-gray-800">
          上海证券交易所行情总览
        </h1>
        <button
          onClick={fetchSSESummary}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          刷新
        </button>
      </div>

      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-100 border-b">
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-6 py-3 text-left text-sm font-semibold text-gray-700 whitespace-nowrap"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.length > 0 ? (
              data.map((row, index) => (
                <tr key={index} className="border-b hover:bg-gray-50 transition-colors">
                  {columns.map((col) => (
                    <td
                      key={`${index}-${col}`}
                      className="px-6 py-4 text-sm text-gray-900"
                    >
                      {formatValue(row[col])}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-6 py-4 text-center text-gray-500">
                  暂无数据
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default StockMarketOverview;
