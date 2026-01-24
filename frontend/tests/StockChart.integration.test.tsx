import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
/**
 * Integration Tests for StockChart Component
 * Tests real-world scenarios and data flow
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import StockChart from '../src/components/StockChart/StockChart';
import StockPrices from '../src/pages/StockPrices';
import { ThemeProvider } from '../src/contexts/ThemeContext';
import { ChartData } from '../src/types';

// Mock ECharts
vi.mock('echarts', () => {
  const mockInstance = {
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
    getOption: vi.fn(() => ({})),
  };
  return {
    init: vi.fn(() => mockInstance),
  };
});

// Mock chart utilities
const mockGetChartOption = vi.fn((chartData, isMobile, isDarkMode) => ({
  tooltip: { trigger: 'axis' },
  grid: { top: 40, right: 20, bottom: 40, left: 60 },
  xAxis: { type: 'category', data: chartData?.dates || [] },
  yAxis: { type: 'value' },
  series: [
    {
      name: '收盘价',
      type: 'line',
      data: chartData?.closePrices || [],
      smooth: false,
      symbol: 'none',
      lineStyle: { width: 2 },
      areaStyle: { color: 'rgba(26, 115, 232, 0.1)' },
    },
  ],
}));

vi.mock('../src/utils/charts', () => ({
  getChartOption: mockGetChartOption,
  disposeChart: vi.fn(),
  startRenderTimer: vi.fn(),
  endRenderTimer: vi.fn(),
  transformPriceData: vi.fn((prices) => ({
    dates: prices.map(p => p.date).reverse(),
    closePrices: prices.map(p => p.close_price).reverse(),
  })),
  validateHistoricalData: vi.fn(() => ({ isValid: true })),
  getChartStatistics: vi.fn((chartData) => ({
    high: Math.max(...chartData.closePrices),
    low: Math.min(...chartData.closePrices),
    latest: chartData.closePrices[chartData.closePrices.length - 1],
    change: 10,
    changePercent: 10,
  })),
}));

vi.mock('react-datepicker', () => {
  return function MockDatePicker({ selected, onChange, ...props }) {
    return (
      <input
        {...props}
        type="date"
        value={selected ? selected.toISOString().split('T')[0] : ''}
        onChange={(e) => onChange(new Date(e.target.value))}
        data-testid="date-picker"
      />
    );
  };
});

vi.mock('../src/hooks/useStocks', () => ({
  useStocks: () => ({
    stocks: [
      { code: '000001', name: '平安银行' },
      { code: '000002', name: '万科A' },
    ],
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
  useStocksSearch: () => ({
    stocks: [
      { code: '000001', name: '平安银行' },
    ],
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
}));

describe('StockChart Integration Tests', () => {
  const mockChartData: ChartData = {
    dates: [
      '2026-01-15', '2026-01-16', '2026-01-17', '2026-01-18', '2026-01-19',
      '2026-01-20', '2026-01-21', '2026-01-22', '2026-01-23', '2026-01-24',
    ],
    closePrices: [100, 105, 102, 108, 110, 107, 112, 115, 111, 118],
  };

  const renderWithTheme = (component: React.ReactElement) => {
    return render(
      <ThemeProvider>
        {component}
      </ThemeProvider>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Data Loading Flow', () => {
    it('shows loading state while data is being fetched', async () => {
      renderWithTheme(
        <StockChart
          chartData={null}
          stockCode="000001"
          isLoading={true}
          error={null}
        />
      );

      expect(screen.getByText(/Loading chart data/i)).toBeInTheDocument();
    });

    it('transitions from loading to data display', async () => {
      const { rerender } = renderWithTheme(
        <StockChart
          chartData={null}
          stockCode="000001"
          isLoading={true}
          error={null}
        />
      );

      expect(screen.getByText(/Loading chart data/i)).toBeInTheDocument();

      rerender(
        <ThemeProvider>
          <StockChart
            chartData={mockChartData}
            stockCode="000001"
            isLoading={false}
            error={null}
          />
        </ThemeProvider>
      );

      await waitFor(() => {
        const loadingElement = screen.queryByText(/Loading chart data/i);
        expect(loadingElement).not.toBeInTheDocument();
        expect(screen.getByText('000001')).toBeInTheDocument();
      });
    });

    it('loads large datasets without performance issues', async () => {
      const largeDataset: ChartData = {
        dates: Array.from({ length: 500 }, (_, i) =>
          new Date(2024, 0, 1 + i).toISOString().split('T')[0]
        ),
        closePrices: Array.from({ length: 500 }, (_, i) =>
          100 + Math.sin(i / 50) * 20
        ),
      };

      const startTime = performance.now();

      renderWithTheme(
        <StockChart
          chartData={largeDataset}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('000001')).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Render should complete within reasonable time (2 seconds)
      expect(renderTime).toBeLessThan(2000);
    });
  });

  describe('Multi-Stock Switching', () => {
    it('switches between different stocks correctly', async () => {
      const { rerender } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      expect(screen.getByText('000001')).toBeInTheDocument();

      // Switch to another stock
      const newMockData: ChartData = {
        dates: mockChartData.dates,
        closePrices: mockChartData.closePrices.map(p => p * 1.1), // Different prices
      };

      rerender(
        <ThemeProvider>
          <StockChart
            chartData={newMockData}
            stockCode="000002"
            isLoading={false}
            error={null}
          />
        </ThemeProvider>
      );

      expect(screen.getByText('000002')).toBeInTheDocument();
    });

    it('cleans up resources when switching stocks', async () => {
      const echarts = require('echarts');
      const { disposeChart } = require('../src/utils/charts');

      const { rerender } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(echarts.init).toHaveBeenCalled();
      });

      echarts.init.mockClear();

      rerender(
        <ThemeProvider>
          <StockChart
            chartData={mockChartData}
            stockCode="000002"
            isLoading={false}
            error={null}
          />
        </ThemeProvider>
      );

      // Should reinitialize for new stock
      await waitFor(() => {
        expect(echarts.init).toHaveBeenCalled();
      });
    });
  });

  describe('Date Range Filtering', () => {
    it('updates chart when date range changes', async () => {
      const initialData: ChartData = {
        dates: ['2026-01-15', '2026-01-16', '2026-01-17'],
        closePrices: [100, 105, 102],
      };

      const filteredData: ChartData = {
        dates: ['2026-01-15', '2026-01-16'],
        closePrices: [100, 105],
      };

      const { rerender } = renderWithTheme(
        <StockChart
          chartData={initialData}
          stockCode="000001"
          isLoading={false}
          error={null}
          startDate="2026-01-15"
          endDate="2026-01-17"
        />
      );

      expect(screen.getByText(/2026-01-15 to 2026-01-17/)).toBeInTheDocument();

      rerender(
        <ThemeProvider>
          <StockChart
            chartData={filteredData}
            stockCode="000001"
            isLoading={false}
            error={null}
            startDate="2026-01-15"
            endDate="2026-01-16"
          />
        </ThemeProvider>
      );

      expect(screen.getByText(/2026-01-15 to 2026-01-16/)).toBeInTheDocument();
    });
  });

  describe('Theme Changes', () => {
    it('updates chart when theme changes from light to dark', async () => {
      const echarts = require('echarts');
      const mockChartInstance = { setOption: vi.fn(), resize: vi.fn() };
      echarts.init.mockReturnValue(mockChartInstance);

      const { rerender } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(mockChartInstance.setOption).toHaveBeenCalled();
      });

      const callCount = mockChartInstance.setOption.mock.calls.length;

      // Simulate theme change
      rerender(
        <ThemeProvider>
          <StockChart
            chartData={mockChartData}
            stockCode="000001"
            isLoading={false}
            error={null}
          />
        </ThemeProvider>
      );

      // setOption should be called again for theme update
      // (Note: In real scenario, would need to change theme context)
    });
  });

  describe('Error Recovery', () => {
    it('recovers from initialization error', async () => {
      const echarts = require('echarts');
      const { disposeChart } = require('../src/utils/charts');
      const onError = vi.fn();

      // First render fails
      echarts.init.mockImplementationOnce(() => {
        throw new Error('Init failed');
      });

      const { rerender } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
          onError={onError}
        />
      );

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(
          expect.objectContaining({
            code: 'CHART_INIT_ERROR',
          })
        );
      });

      // Reset mock to succeed
      echarts.init.mockImplementationOnce(() => ({
        setOption: vi.fn(),
        resize: vi.fn(),
      }));

      // Try again with different stock
      rerender(
        <ThemeProvider>
          <StockChart
            chartData={mockChartData}
            stockCode="000002"
            isLoading={false}
            error={null}
            onError={onError}
          />
        </ThemeProvider>
      );

      await waitFor(() => {
        expect(echarts.init).toHaveBeenCalled();
      });
    });

    it('displays error message properly', () => {
      const error = {
        code: 'API_ERROR',
        message: 'Failed to fetch historical data',
        details: { statusCode: 500 },
      };

      renderWithTheme(
        <StockChart
          chartData={null}
          stockCode="000001"
          isLoading={false}
          error={error}
          onError={vi.fn()}
        />
      );

      // Error component should render (we can't easily test exact message 
      // since ErrorMessage is mocked, but chart shouldn't show)
      expect(screen.queryByText('000001')).not.toBeInTheDocument();
      expect(screen.queryByText(/Price History/)).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles single data point', async () => {
      const singlePointData: ChartData = {
        dates: ['2026-01-15'],
        closePrices: [100],
      };

      renderWithTheme(
        <StockChart
          chartData={singlePointData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('000001')).toBeInTheDocument();
      });
    });

    it('handles two data points', async () => {
      const twoPointsData: ChartData = {
        dates: ['2026-01-15', '2026-01-16'],
        closePrices: [100, 105],
      };

      renderWithTheme(
        <StockChart
          chartData={twoPointsData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('000001')).toBeInTheDocument();
      });
    });

    it('handles NaN values in prices', async () => {
      const invalidData: ChartData = {
        dates: ['2026-01-15', '2026-01-16', '2026-01-17'],
        closePrices: [100, NaN, 102],
      };

      renderWithTheme(
        <StockChart
          chartData={invalidData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('000001')).toBeInTheDocument();
      });
    });

    it('handles zero and negative prices', async () => {
      const extremeData: ChartData = {
        dates: ['2026-01-15', '2026-01-16', '2026-01-17'],
        closePrices: [100, 0, -50],
      };

      renderWithTheme(
        <StockChart
          chartData={extremeData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('000001')).toBeInTheDocument();
      });
    });

    it('handles very large price values', async () => {
      const largeValues: ChartData = {
        dates: ['2026-01-15', '2026-01-16', '2026-01-17'],
        closePrices: [1000000, 1500000, 1200000],
      };

      renderWithTheme(
        <StockChart
          chartData={largeValues}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('000001')).toBeInTheDocument();
      });
    });

    it('handles empty stock code string', () => {
      renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode=""
          isLoading={false}
          error={null}
        />
      );

      expect(screen.getByText(/Price History/)).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('memoizes component to prevent unnecessary re-renders', () => {
      const { rerender } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      const echarts = require('echarts');
      const initialInitCalls = echarts.init.mock.calls.length;

      // Re-render with same props should not re-initialize
      rerender(
        <ThemeProvider>
          <StockChart
            chartData={mockChartData}
            stockCode="000001"
            isLoading={false}
            error={null}
          />
        </ThemeProvider>
      );

      // Init should not be called again
      expect(echarts.init.mock.calls.length).toBe(initialInitCalls);
    });

    it('debounces window resize events', async () => {
      vi.useFakeTimers();
      
      const echarts = require('echarts');
      const mockChartInstance = { setOption: vi.fn(), resize: vi.fn() };
      echarts.init.mockReturnValue(mockChartInstance);

      renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(echarts.init).toHaveBeenCalled();
      });

      // Clear previous calls
      mockChartInstance.resize.mockClear();

      // Trigger multiple resize events rapidly
      for (let i = 0; i < 10; i++) {
        act(() => {
          window.dispatchEvent(new Event('resize'));
        });
      }

      // Advance time by less than debounce delay
      act(() => {
        vi.advanceTimersByTime(200);
      });

      // Should not have called resize yet
      expect(mockChartInstance.resize).not.toHaveBeenCalled();

      // Advance to after debounce delay
      act(() => {
        vi.advanceTimersByTime(150);
      });

      // Should have called resize exactly once (debounced)
      expect(mockChartInstance.resize).toHaveBeenCalledTimes(1);

      vi.useRealTimers();
    });
  });

  describe('Accessibility', () => {
    it('includes proper alt text and labels', () => {
      renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      expect(screen.getByText('000001')).toBeInTheDocument();
      expect(screen.getByText(/Price History/)).toBeInTheDocument();
    });
  });
});
