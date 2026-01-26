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

  const getStatusBadge = (status: 'success' | 'failed') => {
    return status === 'success' ? (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
        成功
      </span>
    ) : (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
        失败
      </span>
    );
  };

  const getCacheStatusBadge = (status: string) => {
    const statusMap = {
      fresh: { text: '最新', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' },
      cached: { text: '缓存', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' },
      stale: { text: '过期', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' }
    };

    const config = statusMap[status as keyof typeof statusMap] || statusMap.cached;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.text}
      </span>
    );
  };

  // Field translations for better display
  const fieldTranslations: Record<string, string> = {
    '最新': '最新价格',
    '股票代码': '股票代码',
    '股票简称': '股票简称',
    '总市值': '总市值',
    '流通市值': '流通市值',
    '市盈率': '市盈率',
    '市净率': '市净率',
    '行业': '行业',
    'org_name_cn': '公司名称',
    'org_short_name_cn': '公司简称',
    'pe_ratio': '市盈率',
    'pb_ratio': '市净率',
    'market_cap': '市值',
    'total_shares': '总股本',
    'circulating_shares': '流通股本',
    'chairman': '董事长',
    'listing_date': '上市日期',
    'province': '省份',
    'sector': '板块'
  };

  const translateField = (field: string): string => {
    return fieldTranslations[field] || field;
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
            股票信息 - {data.stock_code}
          </h2>
          {getCacheStatusBadge(data.cache_status)}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-600 dark:text-gray-400">数据来源状态:</span>
            <div className="mt-1 space-y-1">
              <div className="flex items-center space-x-2">
                <span className="text-gray-700 dark:text-gray-300">东方财富:</span>
                {getStatusBadge(data.source_status.em_api)}
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-gray-700 dark:text-gray-300">雪球:</span>
                {getStatusBadge(data.source_status.xq_api)}
              </div>
            </div>
          </div>

          <div className="md:col-span-2">
            <span className="text-gray-600 dark:text-gray-400">最后更新:</span>
            <div className="mt-1 text-gray-900 dark:text-white font-mono">
              {new Date(data.timestamp).toLocaleString('zh-CN')}
            </div>
          </div>
        </div>
      </div>

      {/* Data display */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          详细信息
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(data.data).map(([key, value]) => (
            <div key={key} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                {translateField(key)}
              </div>
              <div className="text-gray-900 dark:text-white font-mono text-sm break-all">
                {value || '暂无数据'}
              </div>
            </div>
          ))}
        </div>

        {Object.keys(data.data).length === 0 && (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            暂无股票数据
          </div>
        )}
      </div>
    </div>
  );
};

export default StockInfoDisplay;