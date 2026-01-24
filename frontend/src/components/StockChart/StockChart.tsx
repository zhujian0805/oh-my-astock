/**
 * StockChart Component
 * Displays historical price data using Apache ECharts
 * Optimized for large datasets with responsive design and performance tracking
 */

import React, { useRef, useEffect, useCallback } from 'react';
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
  const chartRef = useRef<any>(null);
  const resizeObserverRef = useRef<ResizeObserver | null>(null);
  const isInitializedRef = useRef(false);
  const isReadyRef = useRef(false);
  const { theme } = useTheme();

  // Track if we should render the container
  const hasChartData = !!(chartData && chartData.dates.length > 0);

  // Callback ref - called when DOM is attached
  const containerRef = useCallback((element: HTMLDivElement | null) => {
    if (!element || isInitializedRef.current) {
      return;
    }

    console.log('[StockChart] Container ref callback - element attached');
    isInitializedRef.current = true;

    const initChart = async () => {
      // Wait for DOM to settle
      await new Promise(resolve => setTimeout(resolve, 100));

      if (!element) {
        console.error('[StockChart] Element lost during init');
        isInitializedRef.current = false;
        return;
      }

      // Check dimensions
      const rect = element.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) {
        console.warn('[StockChart] Container has zero dimensions:', {
          width: rect.width,
          height: rect.height,
          offsetWidth: element.offsetWidth,
          offsetHeight: element.offsetHeight
        });
        isInitializedRef.current = false;
        setTimeout(() => initChart(), 100);
        return;
      }

      try {
        console.log('[StockChart] Loading ECharts...');
        const ec = await loadECharts();
        if (!element) {
          isInitializedRef.current = false;
          return;
        }

        console.log('[StockChart] Initializing ECharts instance...');
        chartRef.current = ec.init(element, null, {
          renderer: 'canvas',
          useDirtyRect: true,
          devicePixelRatio: window.devicePixelRatio || 1,
        });
        
        isReadyRef.current = true;
        console.log('[StockChart] Chart ready for data!', {
          hasChart: !!chartRef.current,
          elementDimensions: {
            width: element.offsetWidth,
            height: element.offsetHeight
          }
        });

        // Trigger initial data update if we already have data
        if (hasChartData) {
          console.log('[StockChart] Data already available, updating chart...');
          const isMobile = window.innerWidth < 768;
          const isDarkMode = theme === 'dark';
          const option = getChartOption(chartData, isMobile, isDarkMode);
          chartRef.current.setOption(option, true);
          
          setTimeout(() => {
            if (chartRef.current) {
              chartRef.current.resize();
            }
          }, 50);
        }
      } catch (err) {
        console.error('[StockChart] Failed to initialize:', err);
        isInitializedRef.current = false;
        isReadyRef.current = false;
        if (onError && err instanceof Error) {
          onError({
            code: 'CHART_INIT_ERROR',
            message: 'Failed to initialize chart',
            details: { error: err.message },
          });
        }
      }
    };

    initChart();
  }, [hasChartData, chartData, theme, onError]);

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

  // Set up resize listener
  useEffect(() => {
    let resizeTimeout: NodeJS.Timeout;
    const handleResize = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (chartRef.current) {
          chartRef.current.resize();
        }
      }, 300);
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(resizeTimeout);
    };
  }, []);

  // Update chart data when data or theme changes
  useEffect(() => {
    console.log('[StockChart] Data effect - checking if we should update:', {
      isReady: isReadyRef.current,
      hasChartRef: !!chartRef.current,
      hasChartData,
      dataPoints: chartData?.dates?.length || 0
    });

    // Don't do anything if chart isn't ready or we don't have data
    if (!isReadyRef.current || !chartRef.current || !hasChartData) {
      console.log('[StockChart] Skipping update: ready?', isReadyRef.current, 'has chart?', !!chartRef.current, 'has data?', hasChartData);
      return;
    }

    try {
      const isMobile = window.innerWidth < 768;
      const isDarkMode = theme === 'dark';

      startRenderTimer();
      const option = getChartOption(chartData, isMobile, isDarkMode);
      
      console.log('[StockChart] Setting chart option:', {
        dataPoints: chartData?.dates?.length || 0,
        isMobile,
        isDarkMode,
        seriesCount: Array.isArray(option.series) ? option.series.length : 0
      });

      chartRef.current.setOption(option, true);
      console.log('[StockChart] ✓ Chart option set successfully');

      // Force resize
      setTimeout(() => {
        if (chartRef.current) {
          chartRef.current.resize();
          console.log('[StockChart] ✓ Chart resized');
        }
      }, 50);

      if (chartData) {
        endRenderTimer(chartData.dates.length);
      }
    } catch (err) {
      console.error('[StockChart] Error updating chart:', err);
      if (onError && err instanceof Error) {
        onError({
          code: 'CHART_UPDATE_ERROR',
          message: 'Failed to update chart data',
          details: { error: err.message },
        });
      }
    }
  }, [chartData, theme, onError, hasChartData]); // Update when data or theme changes

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (chartRef.current) {
        disposeChart(chartRef.current);
        chartRef.current = null;
      }
      isInitializedRef.current = false;
      isReadyRef.current = false;
      if (resizeObserverRef.current) {
        resizeObserverRef.current.disconnect();
      }
    };
  }, []);

  // Reset flags when stock code changes
  useEffect(() => {
    isInitializedRef.current = false;
    isReadyRef.current = false;
    if (chartRef.current) {
      disposeChart(chartRef.current);
      chartRef.current = null;
    }
  }, [stockCode]);

  if (error) {
    return <ErrorMessage error={error} />;
  }

  // Determine what to show
  const showLoading = isLoading && !chartData;
  const showEmpty = !isLoading && !hasChartData;

  return (
    <div className="p-2 h-full flex flex-col">
      {/* Header */}
      <div className="mb-2 flex items-baseline justify-between">
        <h2 className="text-lg font-normal text-gray-900 dark:text-white">
          {stockCode} <span className="text-gray-500 dark:text-gray-400 text-sm font-light ml-2">Price History</span>
        </h2>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {startDate && endDate ? `${startDate} to ${endDate}` : 'All available data'}
        </p>
      </div>

      {/* Chart Container - Keep DOM stable by not toggling children */}
      {showLoading ? (
        <div className="flex-1 w-full flex items-center justify-center">
          <LoadingSpinner message="Loading chart data..." />
        </div>
      ) : showEmpty ? (
        <div className="flex-1 w-full flex items-center justify-center">
          <EmptyState
            title="No data available"
            description={
              stockCode
                ? `No historical data available for stock ${stockCode}`
                : 'Select a stock to view price history'
            }
          />
        </div>
      ) : (
        <div
          ref={containerRef}
          className="flex-1 w-full"
          style={{
            minHeight: '300px'
          }}
        />
      )}
    </div>
  );
};

export default React.memo(StockChart);
