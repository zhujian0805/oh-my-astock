/**
 * ECharts Configuration Helper Functions
 * Provides optimized chart configurations for large datasets
 * Includes performance tracking and data validation for 250-750 point datasets
 */

import { ECharts, EChartsOption } from 'echarts';
import { HistoricalPrice, ChartData } from '../types';

// Performance metrics tracking
let renderStartTime = 0;
let renderEndTime = 0;

/**
 * Get optimized ECharts configuration for historical price data
 * Optimized for large datasets (250-750 points) with canvas rendering
 */
export function getChartOption(chartData: ChartData | null, isMobile: boolean = false, isDarkMode: boolean = false): EChartsOption {
  if (!chartData || chartData.dates.length === 0) {
    return getEmptyChartOption(isDarkMode);
  }

  // Data validation
  const isLargeDataset = chartData.dates.length > 500;

  // Colors based on theme
  const textColor = isDarkMode ? '#e5e7eb' : '#374151'; // gray-200 : gray-700
  const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)';
  const lineColor = '#1a73e8';

  // Calculate optimal sampling interval for very large datasets
  const samplingInterval = isLargeDataset ? Math.max(1, Math.floor(chartData.dates.length / 500)) : 1;

  const baseOption: EChartsOption = {
    backgroundColor: 'transparent',
    responsive: true,
    maintainAspectRatio: true,
    animation: false,
    // Optimization: Use sampling for large datasets to reduce data points rendered
    sampling: isLargeDataset ? 'lttb' : undefined,
    tooltip: {
      trigger: 'axis',
      backgroundColor: isDarkMode ? 'rgba(31, 41, 55, 0.9)' : 'rgba(255, 255, 255, 0.9)',
      borderColor: isDarkMode ? '#374151' : '#e5e7eb',
      textStyle: { color: textColor },
      axisPointer: { type: 'line', lineStyle: { color: isDarkMode ? '#9ca3af' : '#6b7280' } },
      formatter: (params: any) => {
        if (!Array.isArray(params) || params.length === 0) return '';
        const param = params[0];
        return `<div class="text-sm">
          <div class="font-semibold">${param.axisValue}</div>
          <div style="color: ${lineColor}">Close: ¥${param.value.toFixed(2)}</div>
        </div>`;
      },
    },
    grid: {
      top: isMobile ? 20 : 40,
      right: isMobile ? 10 : 20,
      bottom: isMobile ? 30 : 40,
      left: isMobile ? 40 : 60,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.dates,
      splitLine: { show: false },
      axisLine: { lineStyle: { color: textColor } },
      axisLabel: {
        color: textColor,
        interval: isMobile ? Math.floor(chartData.dates.length / 4) : (isLargeDataset ? Math.floor(chartData.dates.length / 10) : 'auto'),
        rotate: isMobile ? 45 : 0,
        fontSize: isMobile ? 10 : 12,
        fontFamily: 'Roboto, sans-serif',
      },
    },
    yAxis: {
      type: 'value',
      name: '价格 (¥)',
      nameLocation: 'middle',
      nameGap: isMobile ? 30 : 50,
      splitLine: { lineStyle: { color: gridColor } },
      axisLine: { show: false }, // ECharts yAxis line is hidden by default in many themes, but explicit here
      axisLabel: { color: textColor, fontFamily: 'Roboto, sans-serif' },
      nameTextStyle: { color: textColor }
    },
    series: [
      {
        name: '收盘价',
        type: 'line',
        data: chartData.closePrices,
        smooth: !isLargeDataset,
        symbol: 'none',
        symbolSize: 0,
        lineStyle: { color: lineColor, width: isMobile ? 1.5 : 2 },
        areaStyle: { color: 'rgba(26, 115, 232, 0.1)' },
        // Optimization: use no progressive rendering, rely on canvas for performance
        progressive: isLargeDataset ? 0 : undefined,
      },
    ],
  };

  return baseOption;
}

/**
 * Get empty state chart option
 */
function getEmptyChartOption(isDarkMode: boolean = false): EChartsOption {
  return {
    title: {
      text: 'No Data Available',
      left: 'center',
      top: 'center',
      textStyle: {
        color: isDarkMode ? '#9ca3af' : '#6b7280'
      }
    },
    grid: { top: 40, right: 20, bottom: 40, left: 60 },
    xAxis: { type: 'category' },
    yAxis: { type: 'value' },
    series: [],
  };
}

/**
 * Transform HistoricalPrice array to ChartData
 */
export function transformPriceData(prices: HistoricalPrice[]): ChartData {
  const dates: string[] = [];
  const closePrices: number[] = [];

  // Validate and filter data
  prices.forEach((price) => {
    if (price.date && !isNaN(price.close_price)) {
      dates.push(price.date);
      closePrices.push(price.close_price);
    }
  });

  // Reverse arrays to show data in ascending order (past -> future)
  dates.reverse();
  closePrices.reverse();

  return { dates, closePrices };
}

/**
 * Initialize ECharts instance with canvas renderer for performance
 */
export function initChart(domElement: HTMLElement, option: EChartsOption): ECharts {
  const echarts = (window as any).echarts;
  if (!echarts) {
    throw new Error('ECharts library not loaded');
  }

  const chart = echarts.init(domElement, null, {
    renderer: 'canvas',
    useDirtyRect: true,
  });

  chart.setOption(option);
  return chart;
}

/**
 * Dispose ECharts instance on unmount
 */
export function disposeChart(chart: ECharts | null): void {
  if (chart) {
    chart.dispose();
  }
}

/**
 * Mark render start time for performance metrics
 * Call this when chart render begins (e.g., in useEffect)
 */
export function startRenderTimer(): void {
  renderStartTime = performance.now();
}

/**
 * Mark render end time and log performance metrics
 * Call this when chart render completes (e.g., in resize listener)
 */
export function endRenderTimer(dataPointCount: number): void {
  renderEndTime = performance.now();
  const duration = renderEndTime - renderStartTime;

  // Log performance metrics in development mode
  if (process.env.NODE_ENV === 'development') {
    console.debug(`[Chart Performance] Rendered ${dataPointCount} data points in ${duration.toFixed(2)}ms`, {
      dataPoints: dataPointCount,
      duration: `${duration.toFixed(2)}ms`,
      pointsPerMs: (dataPointCount / duration).toFixed(0),
    });
  }

  return undefined;
}

/**
 * Validate historical price data for chart rendering
 * Returns validation result with message
 */
export function validateHistoricalData(data: HistoricalPrice[]): { isValid: boolean; message?: string } {
  if (!Array.isArray(data)) {
    return { isValid: false, message: 'Data must be an array' };
  }

  if (data.length === 0) {
    return { isValid: false, message: 'No data available' };
  }

  if (data.length > 1000) {
    console.warn(`[Chart Performance] Large dataset detected: ${data.length} points. Performance may be affected.`);
  }

  // Validate data point structure
  const invalidPoints = data.filter(
    (point) => !point.date || typeof point.close_price !== 'number' || isNaN(point.close_price)
  );

  if (invalidPoints.length > 0) {
    console.warn(`[Chart Data Validation] Found ${invalidPoints.length} invalid data points. Filtering them out.`);
  }

  return { isValid: true };
}

/**
 * Get chart statistics from data
 * Useful for displaying High/Low/Latest/Change in UI
 */
export function getChartStatistics(chartData: ChartData): {
  high: number;
  low: number;
  latest: number;
  change: number;
  changePercent: number;
} {
  if (!chartData || chartData.closePrices.length === 0) {
    return { high: 0, low: 0, latest: 0, change: 0, changePercent: 0 };
  }

  const prices = chartData.closePrices;
  const latest = prices[prices.length - 1];
  const earliest = prices[0];
  const high = Math.max(...prices);
  const low = Math.min(...prices);
  const change = latest - earliest;
  const changePercent = earliest !== 0 ? (change / earliest) * 100 : 0;

  return { high, low, latest, change, changePercent };
}

export default {
  getChartOption,
  transformPriceData,
  initChart,
  disposeChart,
  startRenderTimer,
  endRenderTimer,
  validateHistoricalData,
  getChartStatistics,
};
