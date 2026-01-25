# Implementation Plan: Stock Market Frontend Application

**Branch**: `002-stock-frontend` | **Date**: 2026-01-23 | **Spec**: [Feature Specification](spec.md)
**Input**: Feature specification from `/specs/002-stock-frontend/spec.md`

**Note**: This plan is filled in by the `/speckit.plan` command and guides the implementation strategy.

## Summary

Build a React/TypeScript web application with a two-pane layout (sidebar + content area) to visualize Chinese stock historical price data. The MVP (P1) focuses on displaying closing price line charts via Apache ECharts. An extensible sidebar menu architecture (P2) enables future features like stock comparison and financial metrics. The application interfaces with a Python backend API to fetch stock lists and historical data from DuckDB tables (`stock_name_code`, `stock_historical_data`).

## Technical Context

**Language/Version**: TypeScript 5.0+ with React 18+ (modern JSX, hooks, strict mode)
**Primary Dependencies**: React 18, TypeScript 5, Vite 4+, Apache ECharts 5, TailwindCSS 3, Axios (HTTP client)
**Storage**: DuckDB (backend) — frontend uses in-memory React state + optional browser localStorage for UI preferences
**Testing**: Vitest (unit), React Testing Library (component), Playwright (E2E contract testing)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) — responsive from mobile (320px) to desktop (1920px)
**Project Type**: Single-page web application (SPA)
**Performance Goals**:
  - Page load: < 3 seconds on typical network (>1 Mbps)
  - Chart render after stock selection: < 2 seconds
  - User interactions (hover, tooltips): < 100ms response time
  - Support 1-3 years of historical data (250-750 trading days) without lag

**Constraints**:
  - No authentication in MVP; public access assumed
  - Responsive design required (mobile-first approach)
  - No server-side rendering (client-side SPA)
  - All data fetched from backend API (no embedded data)

**Scale/Scope**:
  - 4,000+ Chinese stocks in dropdown
  - 1+ years of historical data per stock (250-750+ data points per chart)
  - Single stock selection and viewing at a time (no multi-stock comparison)
  - Extensible menu for 5-10 future feature additions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Alignment Assessment

**I. Modular Architecture First** ✅ **PASS**
- Frontend will use component-based architecture (React best practice aligned with principle)
- Clear separation: UI components, hooks (state/logic), services (API calls), utilities
- Extensible sidebar menu structure designed from the start (FR-006)

**II. Test-First Discipline (MANDATORY)** ✅ **PASS**
- Will write contract tests for API endpoints and component interactions before implementation
- Unit tests for hooks and utilities using Vitest
- Component tests with React Testing Library
- E2E tests with Playwright for user workflows

**III. Database-Centric Design** ✅ **PASS (N/A for frontend)**
- Not applicable to frontend; backend (Python) owns this principle
- Frontend treats backend API as data source, not directly accessing DuckDB

**IV. Performance & Scalability Built-In** ✅ **PASS**
- Chart rendering optimized: React.memo, useMemo for expensive computations
- Lazy loading: pagination or virtual scrolling for large stock lists (future P3)
- Performance metrics: measure render times, network latency, user interaction response
- Progressive enhancement: basic chart works, enhancements added gradually

**V. Observable & Debuggable Systems** ✅ **PASS**
- Structured logging for API calls, errors, and performance metrics
- React DevTools for state inspection
- Network tab in browser DevTools for API request/response visibility
- Error boundaries for graceful error handling and user feedback
- Debug mode (future): toggle for detailed logging

**Constitutional Violations**: None identified.

**Gate Result**: ✅ **PASSED** — Plan approved for Phase 0 research and Phase 1 design.

## Project Structure

### Documentation (this feature)

```text
specs/002-stock-frontend/
├── plan.md                   # This file (implementation plan)
├── spec.md                   # Feature specification
├── research.md               # Phase 0: API design, library decisions (to be created)
├── data-model.md             # Phase 1: TypeScript types, API contracts (to be created)
├── quickstart.md             # Phase 1: Getting started guide (to be created)
├── contracts/                # Phase 1: API contracts & component specs (to be created)
│   ├── api-contracts.md      # REST endpoint specifications
│   └── component-specs.md    # React component interface definitions
└── checklists/
    └── requirements.md       # Specification quality checklist
```

### Source Code (repository root)

```text
frontend/                      # New frontend application (React/TypeScript/Vite)
├── src/
│   ├── components/           # Reusable React components
│   │   ├── Layout/           # Main layout (sidebar + content pane)
│   │   ├── Sidebar/          # Menu component and menu items
│   │   ├── StockChart/       # Price chart component
│   │   ├── StockSelector/    # Stock dropdown selector
│   │   └── common/           # Shared UI components (LoadingSpinner, Error, etc.)
│   │
│   ├── pages/                # Page/screen components
│   │   ├── StockPrices.tsx   # Stock price visualization page
│   │   └── App.tsx           # Root application component
│   │
│   ├── hooks/                # Custom React hooks
│   │   ├── useStocks.ts      # Fetch and manage stock list
│   │   ├── useHistoricalData.ts # Fetch historical price data
│   │   └── useMenu.ts        # Menu state management
│   │
│   ├── services/             # API service layer
│   │   ├── api.ts            # Axios instance with base URL
│   │   ├── stockService.ts   # Stock data API calls
│   │   └── historicalDataService.ts # Historical price API calls
│   │
│   ├── types/                # TypeScript type definitions
│   │   └── index.ts          # Stock, HistoricalPrice, MenuItem types
│   │
│   ├── utils/                # Utility functions
│   │   ├── formatters.ts     # Date, number formatting
│   │   ├── charts.ts         # ECharts configuration helpers
│   │   └── errors.ts         # Error handling utilities
│   │
│   ├── styles/               # Global styles (TailwindCSS config)
│   │   └── globals.css       # Tailwind directives, custom overrides
│   │
│   └── main.tsx              # Application entry point
│
├── tests/
│   ├── contract/             # Contract tests (API, component interfaces)
│   │   ├── api.spec.ts       # API endpoint contract tests
│   │   └── components.spec.tsx # Component prop/behavior contracts
│   │
│   ├── integration/          # Integration tests (component interaction, API flow)
│   │   ├── StockChart.integration.spec.tsx
│   │   └── StockSelector.integration.spec.tsx
│   │
│   └── e2e/                  # End-to-end tests (Playwright)
│       └── user-flows.spec.ts # User journey tests
│
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
├── tailwind.config.ts        # TailwindCSS configuration
├── package.json              # Project dependencies
├── .env.example              # Environment variable template
└── README.md                 # Frontend-specific documentation
```

**Structure Decision**: Single frontend application (Option 2 variant: web application only, no separate backend in this repo). The frontend is a new project at `frontend/` directory, interfacing with the existing Python backend via REST API. This decision:
- Keeps frontend and backend loosely coupled (different tech stacks, repos later if needed)
- Enables independent deployment and scaling
- Follows web application pattern (separate frontend/backend concerns)
- Aligns with constitutional principle of modular architecture

## Complexity Tracking

> No Constitution Check violations detected. This section intentionally left empty.

---

## Phase 0: Outline & Research

**Status**: To be generated by `/speckit.plan` execution
**Unknowns to Resolve**:
1. Backend API specification (endpoint structure, request/response formats, authentication if added)
2. ECharts best practices for large datasets (250-750+ points)
3. TailwindCSS utility naming conventions and responsive breakpoint strategy
4. React hook patterns for API data fetching (useEffect cleanup, error handling, loading states)
5. TypeScript strict mode with React: prop types, event handler types, context API patterns

**Research Output**: Will be generated in `research.md`

---

## Phase 1: Design & Contracts

**Status**: To be generated by `/speckit.plan` execution
**Outputs**:
1. **data-model.md**: TypeScript type definitions (Stock, HistoricalPrice, MenuItem, ChartData)
2. **contracts/api-contracts.md**: REST API endpoint specifications
3. **contracts/component-specs.md**: React component interface definitions (props, events, state)
4. **quickstart.md**: Getting started guide for developers

**Design Decisions** (pre-research):
- API communication: RESTful JSON via Axios (standard for React apps)
- State management: React hooks + context (no Redux for MVP simplicity)
- Chart library: Apache ECharts for rich, performant visualizations
- Styling: TailwindCSS for rapid UI development and responsive design
- Component pattern: Functional components with hooks (modern React best practice)

---

## Phase 2: Tasks & Implementation

**Status**: Deferred to `/speckit.tasks` command
**Output**: `tasks.md` with implementation tasks organized by user story and phase

---

## Notes

- Constitution check passed; plan is approved for Phase 0/1 execution
- API endpoint structure will be clarified in Phase 0 research based on backend availability
- No external systems required for MVP (single stock selection, no real-time updates)
- ECharts large dataset handling will be researched to ensure performance targets are met
