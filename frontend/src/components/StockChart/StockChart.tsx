/**
 * StockChart Component
 * Displays historical price data using Apache ECharts
 * Optimized for large datasets with responsive design and performance tracking
 */

import React, { useEffect, useRef, useMemo } from 'react';
import { StockChartProps, ChartData } from '../../types';
import { getChartOption, disposeChart, startRenderTimer, endRenderTimer, getChartStatistics } from '../../utils/charts';
import LoadingSpinner from '../common/LoadingSpinner';
import ErrorMessage from '../common/ErrorMessage';
import EmptyState from '../common/EmptyState';
import { useTheme } from '../../contexts/ThemeContext';

/**
 * Dynamic import for ECharts to reduce initial bundle
 */
let echarts: any = null;

const loadECharts = async () => {
  if (!echarts) {
    echarts = await import('echarts');
  }
  return echarts;
};

const StockChart: React.FC<StockChartProps> = ({
  chartData,
  stockCode,
  isLoading = false,
  error = null,
  onError,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const resizeObserverRef = useRef<ResizeObserver | null>(null);
  const { theme } = useTheme();

  // Log chart data changes
  React.useEffect(() => {
    console.log('[StockChart] Chart data updated:', {
      stockCode,
      hasData: !!chartData,
      dataPoints: chartData?.dates?.length || 0,
      isLoading,
      hasError: !!error,
      theme
    });
  }, [chartData, stockCode, isLoading, error, theme]);

  // Initialize and update chart
  useEffect(() => {
    const initChart = async () => {
      // Only skip if container doesn't exist
      if (!containerRef.current) {
        return;
      }

      try {
        startRenderTimer();
        const ec = await loadECharts();

        // Initialize chart if it doesn't exist
        if (!chartRef.current) {
          // Detect mobile view - recalculate on every render to handle resize
          const isMobile = window.innerWidth < 768;

          // Initialize chart
          chartRef.current = ec.init(containerRef.current, null, {
            renderer: 'canvas',
            useDirtyRect: true,
            devicePixelRatio: window.devicePixelRatio || 1,
          });
        }

        const isMobile = window.innerWidth < 768;
        const isDarkMode = theme === 'dark';

        // Set chart option with responsive settings
        const option = getChartOption(chartData, isMobile, isDarkMode);
        chartRef.current.setOption(option, true); // Use notMerge=true to fully replace data

        // Track performance metrics
        if (chartData) {
          endRenderTimer(chartData.dates.length);
        }

        // Log successful render
        if (chartData) {
          console.log(`[StockChart] Chart rendered successfully for ${stockCode} with ${chartData.dates.length} data points`);
        } else {
          console.log(`[StockChart] Chart initialized for ${stockCode} (waiting for data)`);
        }

        if (import.meta.env.VITE_DEBUG) {
          console.log(`[Chart] Rendered ${chartData?.dates?.length || 0} data points for ${stockCode}`);
        }
      } catch (err) {
        console.error('Failed to initialize chart:', err);
        if (onError && err instanceof Error) {
          onError({
            code: 'CHART_INIT_ERROR',
            message: 'Failed to render chart',
            details: { error: err.message },
          });
        }
      }
    };

    initChart();

    // Handle window resize with debounce
    let resizeTimeout: NodeJS.Timeout;
    const handleResize = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (chartRef.current) {
          chartRef.current.resize();
        }
      }, 300); // 300ms debounce
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(resizeTimeout);
    };
  }, [chartData, onError, stockCode, theme]); // Added theme dependency

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (chartRef.current) {
        disposeChart(chartRef.current);
        chartRef.current = null;
      }
      if (resizeObserverRef.current) {
        resizeObserverRef.current.disconnect();
      }
    };
  }, []);

  if (error) {
    return <ErrorMessage error={error} />;
  }

  if (isLoading && !chartData) {
    return <LoadingSpinner message="Loading chart data..." />;
  }

  if (!chartData || chartData.dates.length === 0) {
    return (
      <EmptyState
        title="No data available"
        description={
          stockCode
            ? `No historical data available for stock ${stockCode}`
            : 'Select a stock to view price history'
        }
      />
    );
  }

  return (
    <div className="p-2 h-full flex flex-col">
      {/* Header */}
      <div className="mb-2 flex items-baseline justify-between">
        <h2 className="text-lg font-normal text-gray-900 dark:text-white">
          {stockCode} <span className="text-gray-500 dark:text-gray-400 text-sm font-light ml-2">Price History</span>
        </h2>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Last {chartData.dates.length} days
        </p>
      </div>

      {/* Chart Container */}
      <div
        ref={containerRef}
        className="flex-1 min-h-0 w-full"
      />
    </div>
  );
};

export default React.memo(StockChart);
