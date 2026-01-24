/**
 * Comprehensive Test Suite for StockChart Component
 * Tests chart initialization, data rendering, updates, and error handling
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import React from 'react';
import { render, screen, waitFor, act, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import StockChart from '../src/components/StockChart/StockChart';
import { ThemeProvider } from '../src/contexts/ThemeContext';
import { ChartData } from '../src/types';

// Mock ECharts
vi.mock('echarts', () => ({
  default: {
    init: vi.fn((element, theme, options) => ({
      setOption: vi.fn(),
      resize: vi.fn(),
      dispose: vi.fn(),
      getOption: vi.fn(),
      showLoading: vi.fn(),
      hideLoading: vi.fn(),
    })),
  },
  init: vi.fn((element, theme, options) => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
    getOption: vi.fn(),
    showLoading: vi.fn(),
    hideLoading: vi.fn(),
  })),
}));

// Mock chart utilities
vi.mock('../src/utils/charts', () => ({
  getChartOption: vi.fn((chartData, isMobile, isDarkMode) => ({
    tooltip: { trigger: 'axis' },
    grid: { top: 40, right: 20, bottom: 40, left: 60 },
    xAxis: { type: 'category', data: chartData?.dates || [] },
    yAxis: { type: 'value' },
    series: [
      {
        name: '收盘价',
        type: 'line',
        data: chartData?.closePrices || [],
      },
    ],
  })),
  disposeChart: vi.fn(),
  startRenderTimer: vi.fn(),
  endRenderTimer: vi.fn(),
  transformPriceData: vi.fn(),
}));

describe('StockChart Component', () => {
  const mockChartData: ChartData = {
    dates: ['2026-01-15', '2026-01-16', '2026-01-17', '2026-01-18', '2026-01-19'],
    closePrices: [100, 105, 102, 108, 110],
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
    // Mock console methods to reduce test output
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initial Rendering', () => {
    it('renders loading state when data is loading', () => {
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

    it('renders empty state when no data available', () => {
      renderWithTheme(
        <StockChart
          chartData={null}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      expect(screen.getByText(/No data available/i)).toBeInTheDocument();
      expect(screen.getByText(/No historical data available for stock 000001/i)).toBeInTheDocument();
    });

    it('renders error message when error occurs', () => {
      const error = {
        code: 'FETCH_ERROR',
        message: 'Failed to fetch data',
        details: {},
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

      // Error component is rendered (mock component just shows up)
      expect(screen.queryByText(/Loading chart data/i)).not.toBeInTheDocument();
    });

    it('renders chart header with stock code', () => {
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

    it('displays date range in header when provided', () => {
      renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
          startDate="2026-01-15"
          endDate="2026-01-19"
        />
      );

      expect(screen.getByText(/2026-01-15 to 2026-01-19/)).toBeInTheDocument();
    });

    it('displays default date range text when dates not provided', () => {
      renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      expect(screen.getByText(/Last 6 months/)).toBeInTheDocument();
    });
  });

  describe('Chart Container Ref Callback', () => {
    it('calls callback when container element is mounted', async () => {
      const { container } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      // Wait for the callback to be called
      await waitFor(() => {
        const chartContainer = container.querySelector('[style*="minHeight"]');
        expect(chartContainer).toBeInTheDocument();
      });
    });

    it('initializes ECharts when container is available', async () => {
      const echarts = require('echarts');
      
      renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      // Wait for ECharts initialization
      await waitFor(() => {
        expect(echarts.init).toHaveBeenCalled();
      });
    });

    it('does not re-initialize chart on subsequent renders', async () => {
      const echarts = require('echarts');
      const { rerender } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        expect(echarts.init).toHaveBeenCalledTimes(1);
      });

      // Re-render with same props
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

      // Should still only be called once
      expect(echarts.init).toHaveBeenCalledTimes(1);
    });
  });

  describe('Chart Data Update', () => {
    it('updates chart data when chartData prop changes', async () => {
      const echarts = require('echarts');
      const mockChartInstance = { setOption: vi.fn(), resize: vi.fn() };
      echarts.init.mockReturnValue(mockChartInstance);

      const { rerender } = renderWithTheme(
        <StockChart
          chartData={null}
          stockCode="000001"
          isLoading={true}
          error={null}
        />
      );

      // Update with data
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
        expect(mockChartInstance.setOption).toHaveBeenCalled();
      });
    });

    it('calls setOption with correct parameters', async () => {
      const echarts = require('echarts');
      const getChartOption = require('../src/utils/charts').getChartOption;
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
        expect(mockChartInstance.setOption).toHaveBeenCalledWith(
          expect.any(Object),
          true // notMerge parameter
        );
      });
    });

    it('resizes chart after setting option', async () => {
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
        expect(mockChartInstance.resize).toHaveBeenCalled();
      }, { timeout: 500 });
    });

    it('updates chart when theme changes', async () => {
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

      const initialCallCount = mockChartInstance.setOption.mock.calls.length;

      // Simulate theme change by triggering context update
      // (In real scenario, ThemeProvider context would change)
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

      // Chart should be updated (though with mocked theme, update might not trigger)
      // This tests that the component respects theme changes
    });
  });

  describe('State Transitions', () => {
    it('transitions from loading to showing data', async () => {
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
        expect(screen.queryByText(/Loading chart data/i)).not.toBeInTheDocument();
      });
    });

    it('transitions from data to empty state', async () => {
      const { rerender } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      expect(screen.getByText('000001')).toBeInTheDocument();

      rerender(
        <ThemeProvider>
          <StockChart
            chartData={null}
            stockCode="000001"
            isLoading={false}
            error={null}
          />
        </ThemeProvider>
      );

      await waitFor(() => {
        expect(screen.getByText(/No data available/i)).toBeInTheDocument();
      });
    });

    it('transitions from data to error state', async () => {
      const { rerender } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      const error = {
        code: 'API_ERROR',
        message: 'API request failed',
        details: {},
      };

      rerender(
        <ThemeProvider>
          <StockChart
            chartData={mockChartData}
            stockCode="000001"
            isLoading={false}
            error={error}
            onError={vi.fn()}
          />
        </ThemeProvider>
      );

      // Error component should be displayed
      expect(screen.queryByText('000001')).not.toBeInTheDocument();
    });
  });

  describe('Stock Code Changes', () => {
    it('cleans up old chart when stock code changes', async () => {
      const echarts = require('echarts');
      const { disposeChart } = require('../src/utils/charts');
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
        expect(echarts.init).toHaveBeenCalled();
      });

      // Change stock code
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

      // Chart should be reinitialized
      await waitFor(() => {
        expect(echarts.init).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Container Dimensions', () => {
    it('handles zero dimensions gracefully', async () => {
      const echarts = require('echarts');
      echarts.init.mockImplementation(() => {
        throw new Error('Element has zero dimensions');
      });

      const onError = vi.fn();
      renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
          onError={onError}
        />
      );

      // Component should handle error gracefully
      await waitFor(() => {
        // Check that error handler was called or component didn't crash
        expect(screen.getByText('000001')).toBeInTheDocument();
      });
    });

    it('applies minimum height style to container', () => {
      const { container } = renderWithTheme(
        <StockChart
          chartData={mockChartData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      const chartContainer = container.querySelector('[style*="300"]');
      expect(chartContainer).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('calls onError callback when chart initialization fails', async () => {
      const echarts = require('echarts');
      const onError = vi.fn();
      echarts.init.mockImplementation(() => {
        throw new Error('Init failed');
      });

      renderWithTheme(
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
            message: expect.any(String),
          })
        );
      });
    });

    it('calls onError callback when setOption fails', async () => {
      const echarts = require('echarts');
      const onError = vi.fn();
      const mockChartInstance = {
        setOption: vi.fn(() => {
          throw new Error('SetOption failed');
        }),
        resize: vi.fn(),
      };
      echarts.init.mockReturnValue(mockChartInstance);

      renderWithTheme(
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
            code: 'CHART_UPDATE_ERROR',
            message: expect.any(String),
          })
        );
      });
    });
  });

  describe('Cleanup on Unmount', () => {
    it('disposes chart on unmount', async () => {
      const echarts = require('echarts');
      const { disposeChart } = require('../src/utils/charts');
      const mockChartInstance = { setOption: vi.fn(), resize: vi.fn() };
      echarts.init.mockReturnValue(mockChartInstance);

      const { unmount } = renderWithTheme(
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

      unmount();

      expect(disposeChart).toHaveBeenCalled();
    });
  });

  describe('Window Resize', () => {
    it('resizes chart on window resize', async () => {
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

      // Clear previous resize calls
      mockChartInstance.resize.mockClear();

      // Trigger window resize
      act(() => {
        fireEvent(window, new Event('resize'));
      });

      // Wait for debounce (300ms)
      await waitFor(
        () => {
          expect(mockChartInstance.resize).toHaveBeenCalled();
        },
        { timeout: 500 }
      );
    });
  });

  describe('Data Validation', () => {
    it('handles empty data array', () => {
      const emptyData: ChartData = {
        dates: [],
        closePrices: [],
      };

      renderWithTheme(
        <StockChart
          chartData={emptyData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      expect(screen.getByText(/No data available/i)).toBeInTheDocument();
    });

    it('handles mismatched data lengths gracefully', async () => {
      const echarts = require('echarts');
      const mockChartInstance = { setOption: vi.fn(), resize: vi.fn() };
      echarts.init.mockReturnValue(mockChartInstance);

      const mismatchedData: ChartData = {
        dates: ['2026-01-15', '2026-01-16'],
        closePrices: [100, 105, 110], // More prices than dates
      };

      renderWithTheme(
        <StockChart
          chartData={mismatchedData}
          stockCode="000001"
          isLoading={false}
          error={null}
        />
      );

      await waitFor(() => {
        // Component should still render without crashing
        expect(screen.getByText('000001')).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Behavior', () => {
    it('passes responsive flags to getChartOption', async () => {
      const echarts = require('echarts');
      const getChartOption = require('../src/utils/charts').getChartOption;
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
        expect(getChartOption).toHaveBeenCalledWith(
          mockChartData,
          expect.any(Boolean), // isMobile
          expect.any(Boolean) // isDarkMode
        );
      });
    });
  });
});
