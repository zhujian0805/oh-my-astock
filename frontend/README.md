# Stock Market Frontend Application

A React/TypeScript frontend application for visualizing Chinese stock market data with a focus on historical price trends.

## Features

- **Stock Selection**: Dropdown menu to select from 4,000+ Chinese stocks
- **Historical Price Charts**: Interactive line charts showing closing prices over time
- **Responsive Design**: Mobile-first responsive layout (320px - 1920px)
- **Extensible Menu**: Sidebar menu architecture supporting future features
- **Performance Optimized**: Canvas-based chart rendering for large datasets (250-750 points)

## Tech Stack

- **Framework**: React 18 + TypeScript 5
- **Build Tool**: Vite 4+
- **Styling**: TailwindCSS 3
- **Charts**: Apache ECharts 5
- **HTTP Client**: Axios
- **Testing**: Vitest, React Testing Library, Playwright

## Prerequisites

- Node.js 18+
- npm 9+ or yarn 3+

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` from `.env.example`:
```bash
cp .env.example .env.local
```

4. Update `.env.local` with your backend API URL (default: `http://localhost:8000/api`)

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Code Quality

Run linting:
```bash
npm run lint
```

Fix linting issues:
```bash
npm run lint:fix
```

Format code with Prettier:
```bash
npm run format
```

Type checking:
```bash
npm run type-check
```

## Building

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Testing

Run tests:
```bash
npm run test
```

Run tests with coverage:
```bash
npm run test:coverage
```

Contract tests (API):
```bash
npm run test:contract
```

Integration tests:
```bash
npm run test:integration
```

E2E tests:
```bash
npm run test:e2e
```

## Performance Testing

For comprehensive performance testing guidelines, see [PERFORMANCE_TESTING.md](./PERFORMANCE_TESTING.md).

Quick checklist:
- ✅ Chart renders < 2 seconds for 750+ data points
- ✅ Responsive design tested on mobile (320px), tablet (768px), desktop (1920px)
- ✅ Interaction response time < 100ms
- ✅ Mobile device compatibility (iOS Safari, Android Chrome)

## Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── Layout/          # Main layout (sidebar + content)
│   │   ├── Sidebar/         # Menu and navigation
│   │   ├── StockSelector/   # Stock dropdown selector
│   │   ├── StockChart/      # Historical price chart
│   │   └── common/          # Shared UI components
│   ├── pages/               # Page-level components
│   │   ├── App.tsx          # Root app component
│   │   └── StockPrices.tsx  # Stock prices page
│   ├── hooks/               # Custom React hooks
│   │   ├── useFetch.ts      # Data fetching with caching
│   │   ├── useStocks.ts     # Stock list management
│   │   ├── useHistoricalData.ts # Historical data fetching
│   │   └── useMenu.ts       # Menu state management
│   ├── services/            # API service layer
│   │   ├── api.ts           # Axios instance and config
│   │   ├── stockService.ts  # Stock API calls
│   │   └── historicalDataService.ts # Historical data API
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   │   ├── formatters.ts    # Date/number formatting
│   │   ├── charts.ts        # ECharts helpers
│   │   └── errors.ts        # Error handling
│   ├── styles/              # Global styles
│   │   └── globals.css      # TailwindCSS + custom styles
│   ├── config/              # Configuration files
│   │   └── menu.ts          # Menu configuration
│   └── main.tsx             # Application entry point
├── tests/
│   ├── contract/            # API contract tests
│   ├── integration/         # Component integration tests
│   └── e2e/                 # End-to-end tests
├── public/                  # Static assets
├── package.json             # Dependencies and scripts
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
├── tailwind.config.ts       # TailwindCSS configuration
└── README.md                # This file
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000/api` |
| `VITE_API_TIMEOUT` | Request timeout in ms | `10000` |
| `VITE_ENV` | Environment (development/production) | `development` |
| `VITE_DEBUG` | Enable debug logging | `false` |

## Backend API Requirements

The frontend expects the following API endpoints from the backend:

### Get All Stocks
```
GET /api/stocks?limit=50&offset=0

Response:
{
  "data": [
    {
      "code": "000001",
      "name": "平安银行"
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

### Get Historical Price Data
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

## Performance Targets

- Page load: < 3 seconds (typical network >1 Mbps)
- Chart render: < 2 seconds (750+ data points)
- User interactions: < 100ms response time
- Mobile responsive: 320px to 1920px breakpoints

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

Please see `CONTRIBUTING.md` for code style, commit conventions, and pull request process.

## License

MIT
