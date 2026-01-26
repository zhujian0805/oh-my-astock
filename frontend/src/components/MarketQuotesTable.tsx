/**
 * Market Quotes Table Component
 * Displays market bid-ask data in a table format
 */

import React, { useState, useEffect } from 'react';
import { marketQuotesApi, MarketQuotesResponse } from '../services/marketQuotesApi';

const MarketQuotesTable: React.FC = () => {
  const [data, setData] = useState<MarketQuotesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMarketQuotes();
  }, []);

  const fetchMarketQuotes = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await marketQuotesApi.getMarketQuotes();
      setData(response);
    } catch (err: any) {
      setError(err.message || '获取行情数据失败，请稍后重试');
      console.error('Error fetching market quotes:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price?: number): string => {
    return price ? price.toFixed(2) : '--';
  };

  const formatVolume = (volume?: number): string => {
    if (!volume) return '--';
    if (volume >= 10000) {
      return `${(volume / 10000).toFixed(1)}万`;
    }
    return volume.toString();
  };

  const formatChange = (change?: number | null): { text: string; className: string } => {
    if (change === undefined || change === null) return { text: '--', className: '' };
    const text = change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2);
    const className = change >= 0 ? 'text-red-600' : 'text-green-600';
    return { text, className };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600 dark:text-gray-400">正在获取行情数据...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 dark:text-red-400 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          获取失败
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          {error}
        </p>
        <button
          onClick={fetchMarketQuotes}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
        >
          重试
        </button>
      </div>
    );
  }

  if (!data || !data.quotes.length) {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        暂无行情数据
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
        <span>共 {data.metadata.total_quotes} 只股票</span>
        <span>数据来源: {data.metadata.data_source}</span>
        <span>更新时间: {new Date(data.metadata.last_updated).toLocaleString('zh-CN')}</span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                股票信息
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                最新价
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                涨跌额
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                涨跌幅
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider" colSpan={2}>
                卖盘 (5档)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider" colSpan={2}>
                买盘 (5档)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                成交量
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                成交额
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {data.quotes.map((quote) => (
              <tr key={quote.stock_code} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {quote.stock_name || quote.stock_code}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {quote.stock_code}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {formatPrice(quote.latest_price)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={formatChange(quote.change_amount).className}>
                    {formatChange(quote.change_amount).text}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={formatChange(quote.change_percent).className}>
                    {quote.change_percent ? `${formatChange(quote.change_percent).text}%` : '--'}
                  </span>
                </td>
                {/* Ask prices and volumes */}
                <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {formatPrice(quote.ask_price_1)}
                </td>
                <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {formatVolume(quote.ask_volume_1)}
                </td>
                {/* Bid prices and volumes */}
                <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {formatPrice(quote.bid_price_1)}
                </td>
                <td className="px-3 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {formatVolume(quote.bid_volume_1)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {formatVolume(quote.volume)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {quote.turnover ? `${(quote.turnover / 100000000).toFixed(2)}亿` : '--'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Error display for individual quotes */}
      {data.quotes.some(quote => quote.error) && (
        <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded-md">
          <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200 mb-2">
            部分数据获取失败:
          </h4>
          <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
            {data.quotes.filter(quote => quote.error).map(quote => (
              <li key={quote.stock_code}>
                {quote.stock_code}: {quote.error}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default MarketQuotesTable;