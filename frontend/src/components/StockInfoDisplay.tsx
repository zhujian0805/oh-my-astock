/**
 * Stock Info Display Component
 * Displays merged stock information from both APIs
 */

import React, { useState, useEffect } from 'react';
import { stockInfoApi, StockInfoResponse } from '../services/stockInfoApi';

interface StockInfoDisplayProps {
  stockCode: string;
}

const StockInfoDisplay: React.FC<StockInfoDisplayProps> = ({ stockCode }) => {
  const [data, setData] = useState<StockInfoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (stockCode) {
      fetchStockInfo();
    }
  }, [stockCode]);

  const fetchStockInfo = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await stockInfoApi.getStockInfo(stockCode);
      setData(response);
    } catch (err: any) {
      setError(err.message || '获取股票信息失败，请稍后重试');
      console.error('Error fetching stock info:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (success: boolean) => {
    return success ? (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
        成功
      </span>
    ) : (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
        失败
      </span>
    );
  };

  // Field translations for better display
  const fieldTranslations: Record<string, string> = {
    'name': '股票名称',
    'symbol': '股票代码',
    'exchange': '交易所',
    'industry': '行业',
    'total_market_cap': '总市值',
    'circulating_market_cap': '流通市值',
    'pe_ratio': '市盈率',
    'pb_ratio': '市净率',
    'roe': '净利率',
    'gross_margin': '毛利率',
    'net_margin': '净利率',
    'current_price': '当前价格',
    'change_percent': '涨跌幅',
    'volume': '成交量',
    'turnover': '成交额',
    'high_52w': '52周最高',
    'low_52w': '52周最低',
    'eps': '每股收益',
    'dividend_yield': '股息率'
  };

  const translateField = (field: string): string => {
    return fieldTranslations[field] || field;
  };

  const formatValue = (key: string, value: any): string => {
    if (value === null || value === undefined) return '暂无数据';

    // Format numbers
    if (typeof value === 'number') {
      if (key.includes('price') || key.includes('cap') || key.includes('turnover')) {
        return value.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
      }
      if (key.includes('percent') || key.includes('yield') || key.includes('margin') || key.includes('ratio')) {
        return `${(value * 100).toFixed(2)}%`;
      }
      return value.toLocaleString('zh-CN');
    }

    return String(value);
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">正在获取股票信息...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
        <div className="text-center">
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
            onClick={fetchStockInfo}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header with metadata */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            股票信息 - {data.code}
          </h2>
          <div className="text-sm text-gray-600 dark:text-gray-400">
            更新时间: {new Date(data.last_updated || '').toLocaleString('zh-CN')}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600 dark:text-gray-400">数据来源状态:</span>
            <div className="mt-1 space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-gray-700 dark:text-gray-300">东方财富:</span>
                {getStatusBadge(data.data_sources.east_money)}
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-gray-700 dark:text-gray-300">雪球:</span>
                {getStatusBadge(data.data_sources.xueqiu)}
              </div>
            </div>
          </div>

          {data.errors && data.errors.length > 0 && (
            <div>
              <span className="text-gray-600 dark:text-gray-400">错误信息:</span>
              <div className="mt-1">
                {data.errors.map((error, index) => (
                  <div key={index} className="text-red-600 dark:text-red-400 text-xs">
                    {error}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Data display */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          详细信息
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(data).filter(([key]) =>
            !['code', 'data_sources', 'errors', 'last_updated'].includes(key)
          ).map(([key, value]) => (
            <div key={key} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                {translateField(key)}
              </div>
              <div className="text-gray-900 dark:text-white font-mono text-sm break-all">
                {formatValue(key, value)}
              </div>
            </div>
          ))}
        </div>

        {Object.keys(data).filter(key =>
          !['code', 'data_sources', 'errors', 'last_updated'].includes(key)
        ).length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            暂无股票数据
          </div>
        )}
      </div>
    </div>
  );
};

export default StockInfoDisplay;