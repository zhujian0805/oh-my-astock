/**
 * TypeScript Type Definitions for Stock Market Frontend
 * Defines all data models, API responses, and component interfaces
 */

// ============================================================================
// Domain Models
// ============================================================================

/**
 * Represents a Chinese stock with code and company name
 */
export interface Stock {
  code: string; // e.g., "000001"
  name: string; // e.g., "平安银行"
}

/**
 * Stock list item for dropdown selection
 */
export interface StockListItem {
  id?: number;
  code: string;
  name: string;
  exchange: string;
  is_active?: boolean;
  priority?: number;
  created_at?: string;
}

/**
 * Detailed stock information merged from multiple APIs
 */
export interface StockInfo {
  // Primary key
  code: string;

  // Basic info (precedence: Xueqiu > East Money)
  name?: string;
  symbol?: string;
  exchange?: string;

  // East Money API fields
  industry?: string;
  total_market_cap?: number;
  circulating_market_cap?: number;
  pe_ratio?: number; // East Money preferred
  pb_ratio?: number; // East Money preferred
  roe?: number;
  gross_margin?: number;
  net_margin?: number;

  // Xueqiu API fields
  current_price?: number; // Xueqiu preferred
  change_percent?: number; // Xueqiu preferred
  volume?: number; // Xueqiu preferred
  turnover?: number; // Xueqiu preferred
  high_52w?: number;
  low_52w?: number;
  eps?: number;
  dividend_yield?: number;

  // Metadata
  last_updated?: string;
  data_sources: {
    east_money: boolean;
    xueqiu: boolean;
  };
  errors: string[];
}

/**
 * Market quote with bid-ask data
 */
export interface MarketQuote {
  // Basic identifiers
  code: string;
  name?: string;

  // Bid prices and volumes (5 levels each)
  bid_price_1?: number;
  bid_volume_1?: number;
  bid_price_2?: number;
  bid_volume_2?: number;
  bid_price_3?: number;
  bid_volume_3?: number;
  bid_price_4?: number;
  bid_volume_4?: number;
  bid_price_5?: number;
  bid_volume_5?: number;

  // Ask prices and volumes (5 levels each)
  ask_price_1?: number;
  ask_volume_1?: number;
  ask_price_2?: number;
  ask_volume_2?: number;
  ask_price_3?: number;
  ask_volume_3?: number;
  ask_price_4?: number;
  ask_volume_4?: number;
  ask_price_5?: number;
  ask_volume_5?: number;

  // Market data
  latest_price?: number;
  change_amount?: number;
  change_percent?: number;
  volume?: number;
  turnover?: number;

  // Metadata
  last_updated?: string;
  data_source?: string;
  error?: string;
}

/**
 * Historical price record for a stock on a specific date
 */
export interface HistoricalPrice {
  date: string; // YYYY-MM-DD format
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number; // in shares
  turnover: number; // in RMB
  amplitude: number; // price fluctuation amplitude
  price_change_rate: number; // price change percentage
  price_change: number; // absolute price change
  turnover_rate: number; // turnover rate
}

/**
 * Chart-ready data structure for ECharts
 */
export interface ChartData {
  dates: string[];
  closePrices: number[];
}

/**
 * Sidebar menu item configuration
 */
export interface MenuItem {
  id: string;
  label: string;
  icon?: string;
  component?: React.ComponentType<any>;
  children?: MenuItem[];
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * Pagination metadata in API responses
 */
export interface Pagination {
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

/**
 * Stock list API response
 */
export interface StockListResponse {
  data: Stock[];
  pagination: Pagination;
}

/**
 * Historical price data API response
 */
export interface HistoricalPriceResponse {
  stock_code: string;
  data: HistoricalPrice[];
  metadata: {
    count: number;
    date_range: {
      start: string | null;
      end: string | null;
    } | null;
    filtered: boolean;
  };
}

/**
 * Standard API error response
 */
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  status?: number;
  timestamp?: string;
  path?: string;
}

/**
 * Generic API response wrapper
 */
export interface ApiResponse<T> {
  data: T;
  error?: ApiError;
  timestamp: string;
}

// ============================================================================
// Hook Return Types
// ============================================================================

/**
 * Return type for useFetch hook
 */
export interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  refetch: () => void;
}

/**
 * Return type for useStocks hook
 */
export interface UseStocksReturn extends FetchState<Stock[]> {
  stocks: Stock[];
  isLoading: boolean;
}

/**
 * Return type for useHistoricalData hook
 */
export interface UseHistoricalDataReturn extends FetchState<HistoricalPrice[]> {
  prices: HistoricalPrice[];
  chartData: ChartData | null;
  isLoading: boolean;
}

/**
 * Return type for useMenu hook
 */
export interface UseMenuReturn {
  activeMenuId: string;
  setActiveMenu: (id: string) => void;
  menuItems: MenuItem[];
}

// ============================================================================
// Component Props
// ============================================================================

/**
 * Props for StockSelector component
 */
export interface StockSelectorProps {
  stocks: StockListItem[];
  selectedStock: StockListItem | null;
  onSelect: (stock: StockListItem) => void;
  isLoading?: boolean;
  error?: string | null;
}

/**
 * Props for StockChart component
 */
export interface StockChartProps {
  chartData: ChartData | null;
  stockCode: string;
  isLoading?: boolean;
  error?: ApiError | null;
  onError?: (error: ApiError) => void;
  startDate?: string;
  endDate?: string;
}

/**
 * Props for Sidebar component
 */
export interface SidebarProps {
  items: MenuItem[];
  activeId: string;
  onSelect: (id: string) => void;
  isOpen?: boolean;
  onClose?: () => void;
}

/**
 * Props for MenuItem component
 */
export interface MenuItemProps {
  item: MenuItem;
  isActive: boolean;
  onClick: () => void;
}

/**
 * Props for Layout component
 */
export interface LayoutProps {
  children: React.ReactNode;
  header?: React.ReactNode;
}

/**
 * Props for LoadingSpinner component
 */
export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

/**
 * Props for ErrorMessage component
 */
export interface ErrorMessageProps {
  error: ApiError | string;
  onRetry?: () => void;
}

/**
 * Props for EmptyState component
 */
export interface EmptyStateProps {
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}
