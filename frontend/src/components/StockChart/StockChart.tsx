/**
 * StockChart Component
 * Displays historical price data using Apache ECharts
 * Optimized for large datasets with responsive design and performance tracking
 */

import React, { useRef, useEffect } from 'react';
import { StockChartProps } from '../../types';
import { getChartOption, disposeChart, startRenderTimer, endRenderTimer } from '../../utils/charts';
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
  startDate,
  endDate,
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

  // Initialize chart instance once
  useEffect(() => {
    const initChart = async () => {
      console.log('[StockChart] Attempting to initialize chart...', {
        containerExists: !!containerRef.current,
        chartAlreadyExists: !!chartRef.current
      });

      // Wait longer for DOM to be fully ready
      await new Promise(resolve => setTimeout(resolve, 100));

      // Only skip if container doesn't exist
      if (!containerRef.current) {
        console.error('[StockChart] Container ref is null, cannot initialize chart');
        return;
      }

      // Check if container has dimensions
      const rect = containerRef.current.getBoundingClientRect();
      console.log('[StockChart] Container dimensions:', {
        width: rect.width,
        height: rect.height,
        offsetWidth: containerRef.current.offsetWidth,
        offsetHeight: containerRef.current.offsetHeight
      });

      if (rect.width === 0 || rect.height === 0) {
        console.warn('[StockChart] Container has zero dimensions, retrying in 100ms');
        setTimeout(initChart, 100);
        return;
      }

      try {
        startRenderTimer();
        console.log('[StockChart] Loading ECharts library...');
        const ec = await loadECharts();
        console.log('[StockChart] ECharts loaded successfully');

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

        // Log successful initialization
        console.log(`[StockChart] Chart initialized for ${stockCode}`, {
          chartInstance: !!chartRef.current,
          containerElement: !!containerRef.current,
          containerDimensions: containerRef.current ? {
            width: containerRef.current.offsetWidth,
            height: containerRef.current.offsetHeight
          } : null
        });

        // Ensure chart is properly sized after initialization
        setTimeout(() => {
          if (chartRef.current) {
            chartRef.current.resize();
            console.log('[StockChart] Chart resized after initialization');
          }
        }, 100);

        if (import.meta.env.VITE_DEBUG) {
          console.log(`[Chart] Initialized chart instance for ${stockCode}`);
        }
      } catch (err) {
        console.error('[StockChart] Failed to initialize chart:', err, {
          errorMessage: err instanceof Error ? err.message : String(err),
          errorStack: err instanceof Error ? err.stack : undefined
        });
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
  }, []); // Only run once on mount

  // Update chart data when data or theme changes
  useEffect(() => {
    console.log('[StockChart] Data update effect triggered:', {
      hasChartRef: !!chartRef.current,
      hasChartData: !!chartData,
      stockCode,
      theme,
      chartDataKeys: chartData ? Object.keys(chartData) : [],
      datesLength: chartData?.dates?.length || 0,
      closePricesLength: chartData?.closePrices?.length || 0
    });

    if (!chartRef.current) {
      console.log('[StockChart] Chart not initialized yet, skipping update');
      return; // Chart not initialized yet
    }

    try {
      const isMobile = window.innerWidth < 768;
      const isDarkMode = theme === 'dark';

      // Set chart option with responsive settings
      const option = getChartOption(chartData, isMobile, isDarkMode);
      console.log('[StockChart] Generated chart option:', {
        stockCode,
        hasData: !!chartData,
        dataPoints: chartData?.dates?.length || 0,
        isMobile,
        isDarkMode,
        optionSeries: Array.isArray(option.series) ? option.series.length : (option.series ? 1 : 0),
        optionXAxis: !!option.xAxis,
        optionYAxis: !!option.yAxis
      });

      chartRef.current.setOption(option, true); // Use notMerge=true to fully replace data
      console.log('[StockChart] setOption called successfully');

      // Force resize after setting option to ensure proper rendering
      setTimeout(() => {
        if (chartRef.current) {
          chartRef.current.resize();
          console.log('[StockChart] Chart resized after setOption');
        }
      }, 50);

      // Track performance metrics
      if (chartData) {
        endRenderTimer(chartData.dates.length);
      }

      // Log successful render
      if (chartData) {
        console.log(`[StockChart] Chart updated successfully for ${stockCode} with ${chartData.dates.length} data points`);
      } else {
        console.log(`[StockChart] Chart updated for ${stockCode} (waiting for data)`);
      }

      if (import.meta.env.VITE_DEBUG) {
        console.log(`[Chart] Updated chart with ${chartData?.dates?.length || 0} data points for ${stockCode}`);
      }
    } catch (err) {
      console.error('Failed to update chart:', err);
      if (onError && err instanceof Error) {
        onError({
          code: 'CHART_UPDATE_ERROR',
          message: 'Failed to update chart data',
          details: { error: err.message },
        });
      }
    }
  }, [chartData, stockCode, theme, onError]); // Update when data or theme changes

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

  return (
    <div className="p-2 h-full flex flex-col">
      {/* Header */}
      <div className="mb-2 flex items-baseline justify-between">
        <h2 className="text-lg font-normal text-gray-900 dark:text-white">
          {stockCode} <span className="text-gray-500 dark:text-gray-400 text-sm font-light ml-2">Price History</span>
        </h2>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {startDate && endDate ? `${startDate} to ${endDate}` : 'Last 6 months'}
        </p>
      </div>

      {/* Chart Container - Always render so ref attaches */}
      <div
        ref={containerRef}
        className="flex-1 w-full relative"
        style={{
          minHeight: '300px'
        }}
      >
        {isLoading && !chartData && (
          <div className="absolute inset-0 flex items-center justify-center">
            <LoadingSpinner message="Loading chart data..." />
          </div>
        )}
        
        {!isLoading && (!chartData || chartData.dates.length === 0) && (
          <div className="absolute inset-0 flex items-center justify-center">
            <EmptyState
              title="No data available"
              description={
                stockCode
                  ? `No historical data available for stock ${stockCode}`
                  : 'Select a stock to view price history'
              }
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default React.memo(StockChart);
