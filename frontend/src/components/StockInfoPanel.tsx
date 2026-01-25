import React, { useState, useEffect } from 'react';

interface StockInfo {
  stock_code: string;
  company_name: string;
  industry?: string;
  sector?: string;
  market: string;
  listing_date?: string;
  total_shares?: number;
  circulating_shares?: number;
  market_cap?: number;
  pe_ratio?: number;
  pb_ratio?: number;
  dividend_yield?: number;
  roe?: number;
  roa?: number;
  net_profit?: number;
  total_assets?: number;
  total_liability?: number;
  created_at: string;
  updated_at: string;
}

interface StockInfoPanelProps {
  stockCode: string;
}

export function StockInfoPanel({ stockCode }: StockInfoPanelProps) {
  const [stockInfo, setStockInfo] = useState<StockInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStockInfo();
  }, [stockCode]);

  const fetchStockInfo = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/v1/stocks/${stockCode}/info`);

      if (!response.ok) {
        if (response.status === 404) {
          setError('Stock not found');
        } else if (response.status === 503) {
          setError('Stock information temporarily unavailable');
        } else {
          setError('Failed to load stock information');
        }
        return;
      }

      const data: StockInfo = await response.json();
      setStockInfo(data);
    } catch (err) {
      setError('Network error - please try again later');
      console.error('Error fetching stock info:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value?: number): string => {
    if (value === undefined || value === null) return 'N/A';
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatNumber = (value?: number, decimals: number = 2): string => {
    if (value === undefined || value === null) return 'N/A';
    return new Intl.NumberFormat('zh-CN', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value);
  };

  const formatPercent = (value?: number): string => {
    if (value === undefined || value === null) return 'N/A';
    return `${formatNumber(value, 2)}%`;
  };

  const formatLargeNumber = (value?: number): string => {
    if (value === undefined || value === null) return 'N/A';
    if (value >= 100000000) {
      return `${formatNumber(value / 100000000, 2)}亿`;
    } else if (value >= 10000) {
      return `${formatNumber(value / 10000, 2)}万`;
    }
    return formatNumber(value, 0);
  };

  if (loading) {
    return (
      <div className="stock-info-panel bg-white p-6 rounded-lg shadow-md">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stock-info-panel bg-white p-6 rounded-lg shadow-md">
        <div className="text-center text-gray-500">
          <p className="mb-2">⚠️ {error}</p>
          <button
            onClick={fetchStockInfo}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!stockInfo) {
    return (
      <div className="stock-info-panel bg-white p-6 rounded-lg shadow-md">
        <div className="text-center text-gray-500">
          No stock information available
        </div>
      </div>
    );
  }

  return (
    <div className="stock-info-panel bg-white p-6 rounded-lg shadow-md max-h-96 overflow-y-auto">
      <h3 className="text-xl font-bold mb-4 text-gray-800">
        {stockInfo.company_name}
        <span className="text-sm font-normal text-gray-500 ml-2">
          ({stockInfo.stock_code})
        </span>
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
        {/* Basic Information */}
        <div className="space-y-2">
          <h4 className="font-semibold text-gray-700 border-b pb-1">基本信息</h4>
          <div className="grid grid-cols-2 gap-2">
            <span className="text-gray-600">行业:</span>
            <span className="text-gray-800">{stockInfo.industry || 'N/A'}</span>

            <span className="text-gray-600">板块:</span>
            <span className="text-gray-800">{stockInfo.sector || 'N/A'}</span>

            <span className="text-gray-600">市场:</span>
            <span className="text-gray-800">{stockInfo.market}</span>

            <span className="text-gray-600">上市日期:</span>
            <span className="text-gray-800">{stockInfo.listing_date || 'N/A'}</span>
          </div>
        </div>

        {/* Financial Metrics */}
        <div className="space-y-2">
          <h4 className="font-semibold text-gray-700 border-b pb-1">财务指标</h4>
          <div className="grid grid-cols-2 gap-2">
            <span className="text-gray-600">总市值:</span>
            <span className="text-gray-800">{formatCurrency(stockInfo.market_cap)}</span>

            <span className="text-gray-600">市盈率:</span>
            <span className="text-gray-800">{formatNumber(stockInfo.pe_ratio)}</span>

            <span className="text-gray-600">市净率:</span>
            <span className="text-gray-800">{formatNumber(stockInfo.pb_ratio)}</span>

            <span className="text-gray-600">股息率:</span>
            <span className="text-gray-800">{formatPercent(stockInfo.dividend_yield)}</span>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="space-y-2">
          <h4 className="font-semibold text-gray-700 border-b pb-1">业绩指标</h4>
          <div className="grid grid-cols-2 gap-2">
            <span className="text-gray-600">净资产收益率:</span>
            <span className="text-gray-800">{formatPercent(stockInfo.roe)}</span>

            <span className="text-gray-600">总资产报酬率:</span>
            <span className="text-gray-800">{formatPercent(stockInfo.roa)}</span>

            <span className="text-gray-600">净利润:</span>
            <span className="text-gray-800">{formatCurrency(stockInfo.net_profit)}</span>
          </div>
        </div>

        {/* Capital Structure */}
        <div className="space-y-2">
          <h4 className="font-semibold text-gray-700 border-b pb-1">股本结构</h4>
          <div className="grid grid-cols-2 gap-2">
            <span className="text-gray-600">总股本:</span>
            <span className="text-gray-800">{formatLargeNumber(stockInfo.total_shares)}</span>

            <span className="text-gray-600">流通股本:</span>
            <span className="text-gray-800">{formatLargeNumber(stockInfo.circulating_shares)}</span>

            <span className="text-gray-600">总资产:</span>
            <span className="text-gray-800">{formatCurrency(stockInfo.total_assets)}</span>

            <span className="text-gray-600">总负债:</span>
            <span className="text-gray-800">{formatCurrency(stockInfo.total_liability)}</span>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t text-xs text-gray-500">
        <div className="flex justify-between">
          <span>创建时间: {new Date(stockInfo.created_at).toLocaleString('zh-CN')}</span>
          <span>更新时间: {new Date(stockInfo.updated_at).toLocaleString('zh-CN')}</span>
        </div>
      </div>
    </div>
  );
}