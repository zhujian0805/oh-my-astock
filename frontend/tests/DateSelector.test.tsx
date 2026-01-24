/**
 * Frontend Integration Tests for Date Selector and Chart Rendering
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import StockPrices from '../src/pages/StockPrices';
import { ThemeProvider } from '../src/contexts/ThemeContext';

// Mock the hooks
jest.mock('../src/hooks/useStocks', () => ({
  useStocks: () => ({
    stocks: [
      { code: '000001', name: 'Test Stock 1' },
      { code: '000002', name: 'Test Stock 2' }
    ],
    isLoading: false,
    error: null
  })
}));

jest.mock('../src/hooks/useHistoricalData', () => ({
  useHistoricalData: (stockCode, startDate, endDate) => ({
    chartData: stockCode ? {
      dates: ['2026-01-15', '2026-01-16', '2026-01-17'],
      closePrices: [100, 105, 102]
    } : null,
    prices: stockCode ? [
      { date: '2026-01-15', close_price: 100 },
      { date: '2026-01-16', close_price: 105 },
      { date: '2026-01-17', close_price: 102 }
    ] : [],
    isLoading: false,
    error: null
  })
}));

// Mock DatePicker
jest.mock('react-datepicker', () => {
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

describe('Date Selector and Chart Rendering', () => {
  const renderWithTheme = (component) => {
    return render(
      <ThemeProvider>
        {component}
      </ThemeProvider>
    );
  };

  it('renders stock selector and chart when stock is selected', async () => {
    renderWithTheme(<StockPrices />);

    // Wait for stocks to load
    await waitFor(() => {
      expect(screen.getByText('Select a stock')).toBeInTheDocument();
    });

    // Select a stock
    const stockSelector = screen.getByRole('button', { name: /select a stock/i });
    fireEvent.click(stockSelector);

    const stockOption = screen.getByText('000001 - Test Stock 1');
    fireEvent.click(stockOption);

    // Check if chart renders
    await waitFor(() => {
      expect(screen.getByText('000001')).toBeInTheDocument();
      expect(screen.getByText(/Price History/)).toBeInTheDocument();
    });
  });

  it('filters data when date range is selected', async () => {
    renderWithTheme(<StockPrices />);

    // Select a stock first
    const stockSelector = screen.getByRole('button', { name: /select a stock/i });
    fireEvent.click(stockSelector);

    const stockOption = screen.getByText('000001 - Test Stock 1');
    fireEvent.click(stockOption);

    // Wait for initial chart render
    await waitFor(() => {
      expect(screen.getByText('000001')).toBeInTheDocument();
    });

    // Find date pickers
    const startDatePicker = screen.getAllByTestId('date-picker')[0];
    const endDatePicker = screen.getAllByTestId('date-picker')[1];

    // Select date range
    fireEvent.change(startDatePicker, { target: { value: '2026-01-10' } });
    fireEvent.change(endDatePicker, { target: { value: '2026-01-20' } });

    // The mock should still return data since we can't easily test the actual filtering
    // But we can verify the UI updates
    await waitFor(() => {
      expect(startDatePicker.value).toBe('2026-01-10');
      expect(endDatePicker.value).toBe('2026-01-20');
    });
  });

  it('displays empty state when no stock is selected', () => {
    renderWithTheme(<StockPrices />);

    expect(screen.getByText('Select a Stock')).toBeInTheDocument();
    expect(screen.getByText(/Choose a stock and date range/)).toBeInTheDocument();
  });
});