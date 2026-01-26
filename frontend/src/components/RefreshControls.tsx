/**
 * RefreshControls Component
 * Controls for auto-refresh functionality with interval selection
 */

import React from 'react';

interface RefreshControlsProps {
  isAutoRefreshEnabled: boolean;
  refreshInterval: number;
  isRefreshing: boolean;
  lastRefresh: Date | null;
  onToggleAutoRefresh: () => void;
  onIntervalChange: (interval: number) => void;
  onManualRefresh: () => void;
}

const REFRESH_INTERVALS = [
  { label: '5秒', value: 5 },
  { label: '10秒', value: 10 },
  { label: '15秒', value: 15 },
  { label: '20秒', value: 20 },
  { label: '25秒', value: 25 },
  { label: '30秒', value: 30 },
];

const RefreshControls: React.FC<RefreshControlsProps> = ({
  isAutoRefreshEnabled,
  refreshInterval,
  isRefreshing,
  lastRefresh,
  onToggleAutoRefresh,
  onIntervalChange,
  onManualRefresh,
}) => {
  const formatLastRefresh = (date: Date) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) {
      return `${diffInSeconds}秒前`;
    } else if (diffInSeconds < 3600) {
      return `${Math.floor(diffInSeconds / 60)}分钟前`;
    } else {
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          自动刷新
        </h3>
        <div className="flex items-center space-x-3">
          {/* Manual Refresh Button */}
          <button
            onClick={onManualRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRefreshing ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            ) : (
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            )}
            刷新
          </button>

          {/* Auto Refresh Toggle */}
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              checked={isAutoRefreshEnabled}
              onChange={onToggleAutoRefresh}
              className="rounded border-gray-300 dark:border-gray-600 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
              自动刷新
            </span>
          </label>
        </div>
      </div>

      {/* Auto Refresh Controls */}
      {isAutoRefreshEnabled && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              刷新间隔
            </label>
            <div className="flex flex-wrap gap-2">
              {REFRESH_INTERVALS.map((interval) => (
                <button
                  key={interval.value}
                  onClick={() => onIntervalChange(interval.value)}
                  className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    refreshInterval === interval.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {interval.label}
                </button>
              ))}
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isAutoRefreshEnabled ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
              <span className="text-gray-600 dark:text-gray-400">
                {isAutoRefreshEnabled ? `每 ${refreshInterval} 秒自动刷新` : '自动刷新已关闭'}
              </span>
            </div>
            {lastRefresh && (
              <span className="text-gray-500 dark:text-gray-400">
                最后刷新: {formatLastRefresh(lastRefresh)}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Last Refresh Info (when auto-refresh is disabled) */}
      {!isAutoRefreshEnabled && lastRefresh && (
        <div className="text-sm text-gray-500 dark:text-gray-400">
          最后刷新: {formatLastRefresh(lastRefresh)}
        </div>
      )}
    </div>
  );
};

export default React.memo(RefreshControls);