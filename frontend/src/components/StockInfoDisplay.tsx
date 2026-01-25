/**
 * Stock Info Display Component
 * Displays merged stock information from both APIs
 */

import React from 'react';

interface StockInfoData {
  [key: string]: string;
}

interface SourceStatus {
  em_api: 'success' | 'failed';
  xq_api: 'success' | 'failed';
}

interface StockInfoDisplayProps {
  data: StockInfoData;
  sourceStatus: SourceStatus;
  loading?: boolean;
  error?: string | null;
  className?: string;
}

const StockInfoDisplay: React.FC<StockInfoDisplayProps> = ({
  data,
  sourceStatus,
  loading = false,
  error = null,
  className = '',
}) => {
  if (loading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">加载中...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 bg-red-50 border border-red-200 rounded-md ${className}`}>
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              获取股票信息失败
            </h3>
            <div className="mt-2 text-sm text-red-700">
              {error}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const dataEntries = Object.entries(data);

  if (dataEntries.length === 0) {
    return (
      <div className={`p-4 bg-gray-50 border border-gray-200 rounded-md ${className}`}>
        <p className="text-gray-500 text-center">暂无股票信息</p>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Source Status */}
      <div className="flex space-x-4 text-sm">
        <div className="flex items-center">
          <span className="mr-2">东方财富API:</span>
          <span className={`px-2 py-1 rounded-full text-xs ${
            sourceStatus.em_api === 'success'
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}>
            {sourceStatus.em_api === 'success' ? '成功' : '失败'}
          </span>
        </div>
        <div className="flex items-center">
          <span className="mr-2">雪球API:</span>
          <span className={`px-2 py-1 rounded-full text-xs ${
            sourceStatus.xq_api === 'success'
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}>
            {sourceStatus.xq_api === 'success' ? '成功' : '失败'}
          </span>
        </div>
      </div>

      {/* Data Display */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {dataEntries.map(([key, value]) => (
          <div key={key} className="bg-white p-4 border border-gray-200 rounded-lg shadow-sm">
            <div className="text-sm font-medium text-gray-500 mb-1">
              {key}
            </div>
            <div className="text-lg font-semibold text-gray-900">
              {value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StockInfoDisplay;