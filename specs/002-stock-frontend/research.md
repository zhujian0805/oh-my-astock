# Research: Stock Market Frontend Application

**Date**: 2026-01-23
**Feature**: Stock Market Frontend Application (002-stock-frontend)
**Status**: Phase 0 Complete — All Unknowns Resolved

---

## Executive Summary

Phase 0 research has resolved all technical unknowns identified in the implementation plan. Key decisions:
- **Backend API**: RESTful JSON via Axios (standard for React) with pagination, caching headers, and exponential backoff retry
- **State Management**: React hooks + context (no Redux needed for MVP simplicity)
- **Chart Rendering**: Apache ECharts with canvas renderer for 250-750+ data points
- **Styling**: TailwindCSS with mobile-first responsive design and container queries for extensibility
- **Caching**: Hybrid approach — memory cache + localStorage + HTTP caching headers

---

## 1. React/TypeScript Patterns & Best Practices

### 1.1 React Hook Patterns for Data Fetching

**Decision: Use Custom Hook + Axios**
- Custom `useFetch` hook for reusable API logic (TypeScript-friendly)
- Axios for HTTP client (interceptors, timeout, error handling)
- useEffect with cleanup to prevent memory leaks and race conditions

**Implementation Pattern**:
```typescript
// hooks/useFetch.ts
function useFetch<T>(
  url: string,
  options?: { skip?: boolean; ttl?: number }
): {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  refetch: () => void;
} {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  const cacheRef = useRef<Map<string, { data: T; expiry: number }>>(new Map());

  useEffect(() => {
    let ignore = false;

    if (options?.skip) return;

    const cached = cacheRef.current.get(url);
    if (cached && Date.now() < cached.expiry) {
      setState({ data: cached.data, loading: false, error: null });
      return;
    }

    setState(prev => ({ ...prev, loading: true }));

    apiClient.get<T>(url)
      .then(response => {
        if (!ignore) {
          cacheRef.current.set(url, {
            data: response.data,
            expiry: Date.now() + (options?.ttl || 5 * 60 * 1000)
          });
          setState({ data: response.data, loading: false, error: null });
        }
      })
      .catch(error => {
        if (!ignore) {
          setState({
            data: null,
            loading: false,
            error: error.processedError || { message: 'Unknown error' }
          });
        }
      });

    return () => { ignore = true; };
  }, [url, options?.skip]);

  return {
    ...state,
    refetch: () => {
      cacheRef.current.delete(url);
      // Trigger re-fetch
    }
  };
}
```

**Rationale**:
- Ignore flag prevents memory leaks from stale responses
- Caching reduces API calls and improves UX
- Cleanup function ensures unmounted components don't update state
- Reusable across multiple components

### 1.2 TypeScript with React

**Decision: Strict Mode with Interface-Based Props**

**Component Prop Types**:
```typescript
interface StockChartProps {
  stockCode: string;
  data: HistoricalPrice[];
  onError?: (error: ApiError) => void;
  isLoading?: boolean;
}

const StockChart: React.FC<StockChartProps> = ({ stockCode, data, onError, isLoading }) => {
  // Component implementation
};
```

**Event Handler Types**:
```typescript
const handleSelect: React.ChangeEventHandler<HTMLSelectElement> = (e) => {
  setSelectedStock(e.currentTarget.value);
};

const handleClick: React.MouseEventHandler<HTMLButtonElement> = (e) => {
  e.preventDefault();
  // Handle click
};
```

**Rationale**:
- Strict mode catches errors at compile time
- Interface over type for better tooling support
- Explicit event types prevent runtime errors

### 1.3 State Management Pattern

**Decision: useState for Local UI State + Custom Hook for Server Data**

```typescript
// Global app state context
interface AppContextType {
  selectedStock: Stock | null;
  setSelectedStock: (stock: Stock) => void;
  cachedStocks: Stock[];
}

const AppContext = createContext<AppContextType | undefined>(undefined);

function useAppContext() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useAppContext must be within Provider');
  return context;
}
```

**Rationale**:
- useState for local component state (forms, toggles, UI)
- useContext for cross-component state (selected stock, menu state)
- No Redux overhead for MVP; Redux can be added if complexity grows
- Easier to test and reason about data flow

---

## 2. TailwindCSS Responsive Design & Styling

### 2.1 Layout Strategy: Two-Pane Design

**Decision: Flexbox with CSS Grid Fallback**

**Primary Approach (Flexbox)**:
```html
<div class="flex flex-col md:flex-row h-screen">
  <!-- Sidebar: Full width on mobile, 256px on tablet+ -->
  <aside class="w-full md:w-64 bg-slate-100 border-b md:border-r overflow-y-auto">
    <!-- Menu items -->
  </aside>

  <!-- Content: Full width, fills remaining space -->
  <main class="flex-1 overflow-y-auto">
    <!-- Stock chart and content -->
  </main>
</div>
```

**Responsive Breakpoints Used**:
- Mobile (default): Full-width stacked layout
- `md:` (768px+): Two-pane side-by-side
- `lg:` (1024px+): Enhanced spacing and typography

**Rationale**:
- Flexbox simpler for this layout than grid
- Mobile-first approach ensures mobile UX is not afterthought
- Breakpoint strategy matches target devices (tablets at 768px+)

### 2.2 Component Styling Pattern

**Decision: Utility-First with Component Abstraction**

```typescript
// components/common/Button.tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

const Button: React.FC<ButtonProps> = ({ variant = 'primary', size = 'md', className = '', ...props }) => {
  const baseClass = 'rounded font-semibold transition-colors focus:outline-none';

  const variantClass = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
    danger: 'bg-red-500 text-white hover:bg-red-600'
  }[variant];

  const sizeClass = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  }[size];

  return (
    <button className={`${baseClass} ${variantClass} ${sizeClass} ${className}`} {...props} />
  );
};
```

**Rationale**:
- Extract common patterns into reusable components
- Reduce duplication and improve maintainability
- Easier to apply design consistency
- Simpler to add dark mode later

### 2.3 Accessibility & Focus States

**Decision: ARIA States + Focus Ring Utilities**

```typescript
// components/MenuItem.tsx
<button
  aria-selected={isActive}
  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
             focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
             ${isActive
               ? 'bg-blue-500 text-white aria-selected:bg-blue-600'
               : 'text-gray-700 hover:bg-gray-100'
             }`}
>
  {label}
</button>
```

**Rationale**:
- Focus rings essential for keyboard navigation
- ARIA attributes improve screen reader compatibility
- Visible focus states required for accessibility compliance

---

## 3. Apache ECharts for Large Datasets

### 3.1 Canvas Rendering Strategy

**Decision: Canvas Renderer for 250-750+ Data Points**

```typescript
const initChart = (domElement: HTMLElement) => {
  const chart = echarts.init(domElement, null, {
    renderer: 'canvas',  // Canvas for performance
    useDirtyRect: true   // Dirty rect rendering optimization
  });
  return chart;
};
```

**Chart Configuration**:
```typescript
const getChartOption = (data: HistoricalPrice[]): EChartsOption => ({
  responsive: true,
  maintainAspectRatio: true,
  animation: false,  // No animation for large datasets
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'line' },
    formatter: (params) => {
      if (!Array.isArray(params)) return '';
      const param = params[0];
      return `<div class="text-sm">
        <div class="font-semibold">${formatDate(param.axisValue)}</div>
        <div class="text-blue-600">Close: ¥${param.value}</div>
      </div>`;
    }
  },
  grid: { top: 40, right: 20, bottom: 40, left: 60 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: data.map(d => d.date),
    splitLine: { show: false }
  },
  yAxis: {
    type: 'value',
    name: '价格 (¥)',
    nameLocation: 'middle',
    nameGap: 50
  },
  series: [
    {
      name: '收盘价',
      type: 'line',
      data: data.map(d => d.close_price),
      smooth: true,
      symbol: 'none',  // No symbols for 250+ points
      lineStyle: { color: '#3b82f6', width: 2 },
      areaStyle: { color: 'rgba(59, 130, 246, 0.1)' }
    }
  ]
});
```

**Rationale**:
- Canvas handles 250-750 points without lag
- Dirty rect rendering optimizes re-renders
- No animation needed for static historical data
- Symbol removal reduces rendering overhead

### 3.2 Data Transformation for Performance

**Decision: Pre-Process Data Before Chart Rendering**

```typescript
const prepareChartData = (raw: HistoricalPrice[]): HistoricalPrice[] => {
  // Ensure data is sorted by date
  const sorted = [...raw].sort((a, b) =>
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // Validate and clean
  return sorted.filter(d => d.close_price && !isNaN(d.close_price));
};
```

**Rationale**:
- Data validation reduces chart errors
- Sorting ensures x-axis displays correctly
- Filters out invalid data points

### 3.3 Mobile Responsiveness

**Decision: Responsive Grid + Conditional Chart Options**

```typescript
const getResponsiveChartOption = (data: HistoricalPrice[], isMobile: boolean) => {
  const baseOption = getChartOption(data);

  if (isMobile) {
    return {
      ...baseOption,
      tooltip: {
        ...baseOption.tooltip,
        trigger: 'item' // Touch-friendly
      },
      grid: {
        top: 20,
        right: 10,
        bottom: 30,
        left: 40  // Reduce margins on mobile
      },
      xAxis: {
        ...baseOption.xAxis,
        axisLabel: {
          interval: Math.floor(data.length / 4)  // Show fewer labels
        }
      }
    };
  }

  return baseOption;
};
```

**Rationale**:
- Responsive grid adjusts margins for mobile
- Reduced labels prevent overlap on small screens
- Touch-friendly tooltip handling
- Adapts to viewport size

---

## 4. REST API Design & Backend Integration

### 4.1 API Endpoint Structure

**Decision: Resource-Based RESTful Endpoints**

**Stock Listing Endpoint**:
```
GET /api/stocks?limit=50&offset=0

Response:
{
  "data": [
    {
      "code": "000001",
      "name": "平安银行",
      "market": "shenzhen"
    }
  ],
  "pagination": {
    "total": 5000,
    "limit": 50,
    "offset": 0,
    "hasMore": true
  }
}
```

**Historical Price Endpoint**:
```
GET /api/stocks/{code}/historical?start_date=2025-01-01&end_date=2026-01-23

Response:
{
  "data": [
    {
      "date": "2025-01-02",
      "open_price": 18.40,
      "high_price": 18.75,
      "low_price": 18.35,
      "close_price": 18.50,
      "volume": 2500000,
      "turnover": 46250000
    }
  ]
}
```

**Rationale**:
- RESTful convention aligns with HTTP semantics
- Pagination supports large datasets
- Date range querying enables flexible chart views
- Clean separation of concerns (stocks vs. prices)

### 4.2 Caching Strategy

**Decision: Hybrid Caching — Memory + localStorage + HTTP Headers**

**HTTP Caching Headers**:
- Stock list (metadata): `Cache-Control: max-age=86400, public`
- Historical data (immutable): `Cache-Control: max-age=604800, immutable`
- Real-time quotes (future): `Cache-Control: max-age=300, must-revalidate`

**Memory Cache** (Current Session):
```typescript
// Cache expires after 10 minutes (600,000ms)
const { data: stocks } = useFetch('/api/stocks', { ttl: 10 * 60 * 1000 });
```

**localStorage** (Persistent):
```typescript
// Save frequently accessed stocks
const favoriteStocks = JSON.parse(localStorage.getItem('favoriteStocks') || '[]');
```

**Rationale**:
- Memory cache: Fastest for repeated requests in same session
- localStorage: Persists across page reloads
- HTTP headers: Reduces network bandwidth
- Layered approach balances performance and freshness

### 4.3 Error Handling & Retry Logic

**Decision: Exponential Backoff with Jitter**

```typescript
// axios interceptor
const MAX_RETRIES = 3;
const BASE_DELAY = 1000; // 1 second

apiClient.interceptors.response.use(
  response => response,
  async error => {
    const config = error.config;
    const retryable = [408, 429, 500, 502, 503, 504].includes(error.response?.status);
    const canRetry = retryable && config.retry < MAX_RETRIES;

    if (canRetry) {
      config.retry = (config.retry || 0) + 1;
      const delay = BASE_DELAY * Math.pow(2, config.retry - 1);
      const jitter = Math.random() * 0.1 * delay;

      await new Promise(resolve => setTimeout(resolve, delay + jitter));
      return apiClient(config);
    }

    return Promise.reject(error);
  }
);
```

**User Error Feedback**:
```typescript
// Display user-friendly error messages
const handleFetchError = (error: ApiError) => {
  const messages = {
    'NETWORK_ERROR': 'Network connection failed. Please try again.',
    'INVALID_DATE_RANGE': 'Invalid date range. End date must be after start date.',
    'NOT_FOUND': 'Stock not found. Please select another stock.',
    'RATE_LIMIT_EXCEEDED': 'Too many requests. Please wait a moment.'
  };

  return messages[error.code] || error.message;
};
```

**Rationale**:
- Exponential backoff prevents overwhelming server
- Jitter prevents thundering herd problem
- Retryable status codes: transient failures recover automatically
- User-friendly messages improve UX

---

## 5. Testing Strategy

### 5.1 Contract Tests (API Integration)

**Decision: Vitest + Axios Mock Adapter**

```typescript
// tests/contract/api.spec.ts
import { describe, it, expect, beforeEach } from 'vitest';
import MockAdapter from 'axios-mock-adapter';
import apiClient from '../../src/services/api';

describe('Stock API Contracts', () => {
  let mockAdapter: MockAdapter;

  beforeEach(() => {
    mockAdapter = new MockAdapter(apiClient);
  });

  it('should fetch stocks with pagination', async () => {
    mockAdapter.onGet('/stocks').reply(200, {
      data: [{ code: '000001', name: '平安银行' }],
      pagination: { total: 5000, limit: 50, offset: 0, hasMore: true }
    });

    const response = await apiClient.get('/stocks');
    expect(response.data.pagination).toBeDefined();
    expect(Array.isArray(response.data.data)).toBe(true);
  });
});
```

**Rationale**:
- Mock adapter provides predictable test data
- Tests API contract assumptions before implementation
- Faster than hitting real backend

### 5.2 Component Tests (React Testing Library)

**Decision: User-Centric Testing**

```typescript
// tests/integration/StockChart.integration.spec.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import StockChart from '../../src/components/StockChart';

describe('StockChart Integration', () => {
  it('displays chart when stock data is loaded', async () => {
    render(
      <StockChart
        stockCode="000001"
        data={mockHistoricalData}
        isLoading={false}
      />
    );

    // Chart should render
    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument();
  });

  it('shows tooltip on hover', async () => {
    const user = userEvent.setup();
    render(
      <StockChart
        stockCode="000001"
        data={mockHistoricalData}
        isLoading={false}
      />
    );

    // Hover over chart
    const canvas = screen.getByRole('img', { hidden: true });
    await user.hover(canvas);

    // Tooltip should appear
    await waitFor(() => {
      expect(screen.getByText(/2026-01-23/)).toBeInTheDocument();
    });
  });
});
```

**Rationale**:
- Tests user interactions, not implementation
- Ensures component behaves as expected
- Integration tests catch real-world bugs

---

## 6. Technology Stack Summary

| Category | Decision | Rationale |
|----------|----------|-----------|
| **Framework** | React 18 + TypeScript 5 | Modern, type-safe, widespread ecosystem |
| **Build Tool** | Vite 4+ | Fast development, optimized builds, ES modules |
| **Styling** | TailwindCSS 3 | Utility-first, responsive, no naming conflicts |
| **Charting** | Apache ECharts 5 | Canvas rendering for large datasets, rich interactions |
| **HTTP Client** | Axios | Interceptors, timeout, retry capabilities |
| **State Management** | React Hooks + Context | Lightweight, no Redux overhead for MVP |
| **Testing (Unit)** | Vitest | Fast, Vite-native, ES modules support |
| **Testing (Component)** | React Testing Library | User-centric, best practices |
| **Testing (E2E)** | Playwright | Cross-browser, headless, contract testing |

---

## 7. Architecture Decisions Summary

| Decision | Chosen | Alternatives Considered | Why |
|----------|--------|------------------------|-----|
| **State Management** | Hooks + Context | Redux, Zustand, Jotai | Simpler for MVP; Redux adds overhead; scales if needed |
| **Chart Rendering** | Canvas | SVG, Recharts | Canvas handles 250-750 points better; performance critical |
| **Caching** | Custom Hook | React Query, SWR | Sufficient for current scope; can upgrade if complexity grows |
| **API Communication** | RESTful JSON | GraphQL, gRPC | REST is simpler; GraphQL adds complexity not needed yet |
| **Layout** | Flexbox | CSS Grid | Flexbox simpler for two-pane; grid better for multi-column |

---

## 8. Open Questions Resolved

### ✅ API Endpoint Structure
**Resolved**: RESTful JSON API with pagination, date range filtering, and HTTP caching headers as documented above.

### ✅ ECharts Large Dataset Handling
**Resolved**: Canvas rendering with data validation and responsive options; 750+ points render smoothly without animation.

### ✅ TailwindCSS Strategy
**Resolved**: Mobile-first responsive design with md/lg breakpoints; component abstraction for maintainability.

### ✅ React Hook Patterns
**Resolved**: Custom `useFetch` hook for data fetching with caching; useContext for cross-component state; TypeScript strict mode.

### ✅ Data Caching
**Resolved**: Hybrid approach with memory cache (5-10min TTL), localStorage (persistent), and HTTP caching headers.

---

## Next Steps: Phase 1 Design

Research complete. Ready to proceed with Phase 1 to generate:
1. **data-model.md**: TypeScript type definitions
2. **contracts/api-contracts.md**: REST endpoint specifications
3. **contracts/component-specs.md**: React component interfaces
4. **quickstart.md**: Developer onboarding guide
