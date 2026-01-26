/**
 * StockInfoDisplay Component Tests
 * Tests the display of merged stock information from both APIs
 */

import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import axios from 'axios';
import StockInfoDisplay from '../frontend/src/components/StockInfoDisplay';

// Mock axios
vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('StockInfoDisplay', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays loading state initially', async () => {
    // Mock pending API call
    mockedAxios.get.mockImplementation(() => new Promise(() => {}));

    render(<StockInfoDisplay stockCode="000001" />);

    expect(screen.getByText('正在获取股票信息...')).toBeInTheDocument();
  });

  it('displays stock information when API succeeds', async () => {
    const mockData = {
      stock_code: '000001',
      data: {
        '股票代码': '000001',
        '股票简称': '平安银行',
        '最新': '10.5',
        '总市值': '2000000000'
      },
      source_status: {
        em_api: 'success',
        xq_api: 'success'
      },
      timestamp: '2026-01-26T10:30:00Z',
      cache_status: 'fresh'
    };

    mockedAxios.get.mockResolvedValue({ data: mockData });

    render(<StockInfoDisplay stockCode="000001" />);

    await waitFor(() => {
      expect(screen.getByText('股票信息 - 000001')).toBeInTheDocument();
    });

    expect(screen.getByText('平安银行')).toBeInTheDocument();
    expect(screen.getByText('10.5')).toBeInTheDocument();
    expect(screen.getByText('成功')).toBeInTheDocument();
  });

  it('displays partial data when one API fails', async () => {
    const mockData = {
      stock_code: '000001',
      data: {
        '股票代码': '000001',
        '股票简称': '平安银行'
      },
      source_status: {
        em_api: 'success',
        xq_api: 'failed'
      },
      timestamp: '2026-01-26T10:30:00Z',
      cache_status: 'fresh'
    };

    mockedAxios.get.mockResolvedValue({ data: mockData });

    render(<StockInfoDisplay stockCode="000001" />);

    await waitFor(() => {
      expect(screen.getByText('股票信息 - 000001')).toBeInTheDocument();
    });

    // Should show success for EM and failure for XQ
    const statusElements = screen.getAllByText('成功');
    const failureElements = screen.getAllByText('失败');
    expect(statusElements.length).toBeGreaterThan(0);
    expect(failureElements.length).toBeGreaterThan(0);
  });

  it('displays error message when API fails', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { status: 404, data: { detail: 'Stock data not available' } }
    });

    render(<StockInfoDisplay stockCode="999999" />);

    await waitFor(() => {
      expect(screen.getByText('未找到该股票信息')).toBeInTheDocument();
    });

    expect(screen.getByText('重试')).toBeInTheDocument();
  });

  it('displays generic error for other failures', async () => {
    mockedAxios.get.mockRejectedValue({
      response: { status: 500 }
    });

    render(<StockInfoDisplay stockCode="000001" />);

    await waitFor(() => {
      expect(screen.getByText('获取股票信息失败，请稍后重试')).toBeInTheDocument();
    });
  });

  it('translates field names correctly', async () => {
    const mockData = {
      stock_code: '000001',
      data: {
        '最新': '10.5',
        '股票代码': '000001',
        'org_name_cn': '平安银行'
      },
      source_status: {
        em_api: 'success',
        xq_api: 'success'
      },
      timestamp: '2026-01-26T10:30:00Z',
      cache_status: 'fresh'
    };

    mockedAxios.get.mockResolvedValue({ data: mockData });

    render(<StockInfoDisplay stockCode="000001" />);

    await waitFor(() => {
      expect(screen.getByText('最新价格')).toBeInTheDocument();
      expect(screen.getByText('公司名称')).toBeInTheDocument();
    });
  });

  it('shows empty state when no data is available', async () => {
    const mockData = {
      stock_code: '000001',
      data: {},
      source_status: {
        em_api: 'success',
        xq_api: 'success'
      },
      timestamp: '2026-01-26T10:30:00Z',
      cache_status: 'fresh'
    };

    mockedAxios.get.mockResolvedValue({ data: mockData });

    render(<StockInfoDisplay stockCode="000001" />);

    await waitFor(() => {
      expect(screen.getByText('暂无股票数据')).toBeInTheDocument();
    });
  });

  it('displays cache status correctly', async () => {
    const mockData = {
      stock_code: '000001',
      data: { '股票代码': '000001' },
      source_status: { em_api: 'success', xq_api: 'success' },
      timestamp: '2026-01-26T10:30:00Z',
      cache_status: 'cached'
    };

    mockedAxios.get.mockResolvedValue({ data: mockData });

    render(<StockInfoDisplay stockCode="000001" />);

    await waitFor(() => {
      expect(screen.getByText('缓存')).toBeInTheDocument();
    });
  });
});