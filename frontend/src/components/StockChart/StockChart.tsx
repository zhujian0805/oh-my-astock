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

/**
 * Dynamic import for ECharts to reduce initial bundle
 */
let echarts: any = null;

const loadECharts = async () => {
  if (!echarts) {
    echarts = (await import('echarts')).default;
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

  // Initialize and update chart
  useEffect(() => {
    const initChart = async () => {
      if (!containerRef.current || !chartData) {
        return;
      }

      try {
        startRenderTimer();
        const ec = await loadECharts();

        // Dispose old chart
        if (chartRef.current) {
          disposeChart(chartRef.current);
        }

        // Detect mobile view - recalculate on every render to handle resize
        const isMobile = window.innerWidth < 768;

        // Initialize chart
        chartRef.current = ec.init(containerRef.current, null, {
          renderer: 'canvas',
          useDirtyRect: true,
          devicePixelRatio: window.devicePixelRatio || 1,
        });

        // Set chart option with responsive settings
        const option = getChartOption(chartData, isMobile);
        chartRef.current.setOption(option);

        // Track performance metrics
        endRenderTimer(chartData.dates.length);

        if (import.meta.env.VITE_DEBUG) {
          console.log(`[Chart] Rendered ${chartData.dates.length} data points for ${stockCode}`);
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
  }, [chartData, onError, stockCode]);

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

  if (isLoading) {
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

  // Memoize chart statistics to avoid recalculation on every render
  const stats = useMemo(() => getChartStatistics(chartData), [chartData]);

  return (
    <div className="p-6 h-full flex flex-col">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-900">
          {stockCode} - Price History
        </h2>
        <p className="text-sm text-gray-600">
          {chartData.dates.length} trading days
        </p>
      </div>

      {/* Chart Container */}
      <div
        ref={containerRef}
        className="flex-1 min-h-0 bg-white rounded-lg border border-gray-200"
      />

      {/* Footer Stats - Using memoized calculations */}
      {chartData.closePrices.length > 0 && (
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-xs text-gray-600">High</p>
            <p className="text-lg font-semibold text-gray-900">
              ¥{stats.high.toFixed(2)}
            </p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-xs text-gray-600">Low</p>
            <p className="text-lg font-semibold text-gray-900">
              ¥{stats.low.toFixed(2)}
            </p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-xs text-gray-600">Latest</p>
            <p className="text-lg font-semibold text-gray-900">
              ¥{stats.latest.toFixed(2)}
            </p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-xs text-gray-600">Change</p>
            <p className={`text-lg font-semibold ${
              stats.changePercent >= 0
                ? 'text-green-600'
                : 'text-red-600'
            }`}>
              {stats.changePercent.toFixed(2)}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default React.memo(StockChart);
