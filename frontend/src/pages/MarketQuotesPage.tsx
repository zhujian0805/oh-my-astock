import React, { useState, useEffect, useCallback } from 'react';
import MultiStockSelector from '../components/MultiStockSelector';
import RefreshControls from '../components/RefreshControls';
import MarketQuotesTable from '../components/MarketQuotesTable';
import { marketQuotesApi, MarketQuotesResponse } from '../services/marketQuotesApi';
import { StockListItem } from '../types';

// Storage keys
const STORAGE_SELECTED_STOCKS = 'market-quotes-selected-stocks';
const STORAGE_AUTO_REFRESH = 'market-quotes-auto-refresh';
const STORAGE_REFRESH_INTERVAL = 'market-quotes-refresh-interval';

// Default stocks (fallback)
const DEFAULT_STOCKS = ['000001', '600000', '000002', '600036', '000858'];

const MarketQuotesPage: React.FC = () => {
  // Data state
  const [marketData, setMarketData] = useState<MarketQuotesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  // Stock selection state
  const [selectedStocks, setSelectedStocks] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_SELECTED_STOCKS);
      return stored ? JSON.parse(stored) : DEFAULT_STOCKS;
    } catch {
      return DEFAULT_STOCKS;
    }
  });

  const [availableStocks, setAvailableStocks] = useState<StockListItem[]>([]);
  const [stocksLoading, setStocksLoading] = useState(false);

  // Auto-refresh state
  const [isAutoRefreshEnabled, setIsAutoRefreshEnabled] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_AUTO_REFRESH);
      return stored ? JSON.parse(stored) : false;
    } catch {
      return false;
    }
  });

  const [refreshInterval, setRefreshInterval] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_REFRESH_INTERVAL);
      return stored ? parseInt(stored, 10) : 10;
    } catch {
      return 10;
    }
  });

  const [isRefreshing, setIsRefreshing] = useState(false);

  // Load available stocks
  useEffect(() => {
    const loadAvailableStocks = async () => {
      setStocksLoading(true);
      try {
        const response = await fetch('/api/stocks?limit=1000'); // Get up to 1000 stocks
        const data = await response.json();
        // Map Stock[] to StockListItem[] by adding exchange field
        const stocksWithExchange: StockListItem[] = data.data.map((stock: { code: string; name: string }) => ({
          ...stock,
          exchange: stock.code.startsWith('6') ? 'SH' : 'SZ', // 6xxxx = Shanghai, others = Shenzhen
        }));
        setAvailableStocks(stocksWithExchange);
      } catch (err) {
        console.error('Failed to load stocks:', err);
        // Fallback to mock data if API fails
        const mockStocks: StockListItem[] = [
          { code: '000001', name: '平安银行', exchange: 'SZ' },
          { code: '000002', name: '万科A', exchange: 'SZ' },
          { code: '000858', name: '五粮液', exchange: 'SZ' },
          { code: '600000', name: '浦发银行', exchange: 'SH' },
          { code: '600036', name: '招商银行', exchange: 'SH' },
          { code: '600519', name: '贵州茅台', exchange: 'SH' },
          { code: '000568', name: '泸州老窖', exchange: 'SZ' },
          { code: '600276', name: '恒瑞医药', exchange: 'SH' },
          { code: '000538', name: '云南白药', exchange: 'SZ' },
          { code: '600887', name: '伊利股份', exchange: 'SH' },
          { code: '000725', name: '京东方A', exchange: 'SZ' },
          { code: '002142', name: '宁波银行', exchange: 'SZ' },
          { code: '600309', name: '万华化学', exchange: 'SH' },
          { code: '000776', name: '广发证券', exchange: 'SZ' },
          { code: '600606', name: '绿地控股', exchange: 'SH' },
        ];
        setAvailableStocks(mockStocks);
      } finally {
        setStocksLoading(false);
      }
    };

    loadAvailableStocks();
  }, []);

  // Fetch market data
  const fetchMarketData = useCallback(async () => {
    if (selectedStocks.length === 0) {
      setMarketData(null);
      setError(null);
      return;
    }

    setIsRefreshing(true);
    setError(null);

    try {
      const stocksParam = selectedStocks.join(',');
      const response = await marketQuotesApi.getMarketQuotes(stocksParam);
      setMarketData(response);
      setLastRefresh(new Date());
    } catch (err: any) {
      setError(err.message || '获取行情数据失败');
      console.error('Error fetching market data:', err);
    } finally {
      setIsRefreshing(false);
    }
  }, [selectedStocks]);

  // Manual refresh
  const handleManualRefresh = useCallback(() => {
    fetchMarketData();
  }, [fetchMarketData]);

  // Auto-refresh effect
  useEffect(() => {
    if (!isAutoRefreshEnabled) return;

    const interval = setInterval(() => {
      fetchMarketData();
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [isAutoRefreshEnabled, refreshInterval, fetchMarketData]);

  // Initial data load
  useEffect(() => {
    fetchMarketData();
  }, []); // Only run once on mount

  // Handle stock selection changes
  const handleStockSelectionChange = useCallback((stockCodes: string[]) => {
    setSelectedStocks(stockCodes);
    // Persist to localStorage
    localStorage.setItem(STORAGE_SELECTED_STOCKS, JSON.stringify(stockCodes));
  }, []);

  // Handle auto-refresh toggle
  const handleToggleAutoRefresh = useCallback(() => {
    const newValue = !isAutoRefreshEnabled;
    setIsAutoRefreshEnabled(newValue);
    localStorage.setItem(STORAGE_AUTO_REFRESH, JSON.stringify(newValue));
  }, [isAutoRefreshEnabled]);

  // Handle refresh interval change
  const handleIntervalChange = useCallback((interval: number) => {
    setRefreshInterval(interval);
    localStorage.setItem(STORAGE_REFRESH_INTERVAL, interval.toString());
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        行情报价
      </h1>

      <div className="space-y-6">
        {/* Stock Selector */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            股票选择
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            选择您想要关注的股票，系统将显示其实时行情数据
          </p>
          <MultiStockSelector
            stocks={availableStocks}
            selectedStocks={selectedStocks}
            onSelectionChange={handleStockSelectionChange}
            isLoading={stocksLoading}
            error={null}
          />
        </div>

        {/* Refresh Controls */}
        <RefreshControls
          isAutoRefreshEnabled={isAutoRefreshEnabled}
          refreshInterval={refreshInterval}
          isRefreshing={isRefreshing}
          lastRefresh={lastRefresh}
          onToggleAutoRefresh={handleToggleAutoRefresh}
          onIntervalChange={handleIntervalChange}
          onManualRefresh={handleManualRefresh}
        />

        {/* Market Data Table */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="mb-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              当前市场行情
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              显示股票的实时买卖盘价格和交易信息
            </p>
          </div>

          <MarketQuotesTable
            data={marketData}
            loading={loading || isRefreshing}
            error={error}
            onRetry={handleManualRefresh}
          />
        </div>
      </div>
    </div>
  );
};

export default MarketQuotesPage;