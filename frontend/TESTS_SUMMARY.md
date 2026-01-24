# StockChart Component Test Suite

## Overview
Comprehensive test suite for the StockChart component covering all changes made to fix the chart rendering issue.

## Test Files Created

### 1. `tests/StockChart.test.tsx` - Unit Tests
**Purpose**: Test individual StockChart component functionality

**Test Coverage**:
- **Initial Rendering**
  - Loading state display
  - Empty state display when no data
  - Error message display
  - Header with stock code
  - Date range display

- **Chart Container Ref Callback**
  - Callback invocation when container mounted
  - ECharts initialization
  - No re-initialization on re-renders
  - Container ref stability

- **Chart Data Update**
  - Chart data updates when prop changes
  - Correct setOption parameters
  - Chart resize after option set
  - Theme change triggering updates

- **State Transitions**
  - Loading → Data display
  - Data → Empty state
  - Data → Error state

- **Stock Code Changes**
  - Old chart cleanup
  - Chart reinitialization for new stock

- **Container Dimensions**
  - Graceful handling of zero dimensions
  - Minimum height styling

- **Error Handling**
  - onError callback on initialization failure
  - onError callback on setOption failure
  - Error message display

- **Cleanup on Unmount**
  - Chart disposal on unmount
  - Resource cleanup

- **Window Resize**
  - Debounced resize handling
  - Proper resize timing (300ms debounce)

- **Data Validation**
  - Empty data array handling
  - Mismatched data lengths
  - NaN value handling

- **Responsive Behavior**
  - isMobile flag passed to getChartOption
  - isDarkMode flag passed to getChartOption

### 2. `tests/StockChart.integration.test.tsx` - Integration Tests
**Purpose**: Test real-world scenarios and complex interactions

**Test Coverage**:
- **Data Loading Flow**
  - Loading state display
  - Loading to data transition
  - Large dataset performance (500+ points)

- **Multi-Stock Switching**
  - Switching between different stocks
  - Resource cleanup during switches

- **Date Range Filtering**
  - Chart update on date range change
  - Date range display updates

- **Theme Changes**
  - Chart update on theme change (light/dark)

- **Error Recovery**
  - Recovery from initialization errors
  - Recovery with different stock after error
  - Error message display

- **Edge Cases**
  - Single data point
  - Two data points
  - NaN values in prices
  - Zero and negative prices
  - Very large price values
  - Empty stock code

- **Performance Tests**
  - Component memoization (memo wrapper)
  - Window resize debouncing
  - Render time < 2 seconds for large datasets

- **Accessibility**
  - Proper labels and text content
  - Stock code visibility
  - Price History header visibility

## Test Environment

### Technologies
- **Testing Framework**: Vitest (configured in `vite.config.ts`)
- **Component Testing**: React Testing Library
- **Mocking**: Vitest's `vi` module

### Configuration
```typescript
// In vite.config.ts
test: {
  globals: true,
  environment: 'jsdom',
  setupFiles: [],
  include: ['tests/**/*.{test,spec}.{ts,tsx}'],
  exclude: ['node_modules'],
}
```

## Running Tests

### Install Dependencies
```bash
npm install
```

### Run All Tests
```bash
npm test
```

### Run Specific Test File
```bash
npm test -- tests/StockChart.test.tsx
```

### Run with UI
```bash
npm run test:ui
```

### Generate Coverage Report
```bash
npm run test:coverage
```

## Test Scenarios Covered

### Chart Initialization (Critical Path)
1. ✅ Container ref callback fires when DOM attached
2. ✅ ECharts instance created with proper options
3. ✅ Chart ready for data updates
4. ✅ No re-initialization on subsequent renders
5. ✅ Proper cleanup on unmount

### Data Update Flow
1. ✅ Data triggers chart update via useEffect
2. ✅ Chart uses isReadyRef to gate updates
3. ✅ setOption called with notMerge=true
4. ✅ Chart resize called after data update
5. ✅ Performance metrics tracked

### State Management
1. ✅ hasChartData boolean computed correctly
2. ✅ isInitializedRef prevents duplicate initialization
3. ✅ isReadyRef gates data updates
4. ✅ Flags reset on stock code change
5. ✅ Flags reset on unmount

### Error Handling
1. ✅ Initialize errors caught and reported
2. ✅ Update errors caught and reported
3. ✅ Component continues to function after errors
4. ✅ Error callbacks invoked correctly

### Responsive Behavior
1. ✅ Mobile detection (innerWidth < 768)
2. ✅ Dark mode detection (theme === 'dark')
3. ✅ Window resize debounced (300ms)
4. ✅ Chart resizes on window resize

### Edge Cases
1. ✅ Single data point
2. ✅ Two data points
3. ✅ Empty dataset
4. ✅ Large dataset (500+ points)
5. ✅ NaN values
6. ✅ Negative prices
7. ✅ Very large values

## Key Improvements Tested

### Original Problem
- Chart ref callback runs before DOM attached
- Chart initialization skipped when ref is null
- No data update mechanism after init

### Solution Verified by Tests
- ✅ useCallback ref triggers when DOM attached
- ✅ Element dimensions checked before init
- ✅ isReadyRef flag gates data updates
- ✅ Data update effect runs after chart ready
- ✅ Safe cleanup on stock/unmount changes

## Mock Strategy

### ECharts Mock
```typescript
vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
  })),
}));
```

### Chart Utils Mock
```typescript
vi.mock('../src/utils/charts', () => ({
  getChartOption: vi.fn((chartData, isMobile, isDarkMode) => ({...})),
  disposeChart: vi.fn(),
  startRenderTimer: vi.fn(),
  endRenderTimer: vi.fn(),
}));
```

## Test Statistics

- **Total Test Files**: 2
- **Test Cases**: 50+
- **Code Coverage Areas**:
  - Component initialization
  - Data rendering
  - State updates
  - Error handling
  - Performance
  - Accessibility

## Notes for Developers

1. **Running Tests Locally**
   - Ensure `jsdom` is installed for DOM testing
   - Tests mock ECharts for isolation
   - No real chart rendering in tests

2. **Adding New Tests**
   - Use `describe()` for grouping
   - Use `it()` for individual tests
   - Use `waitFor()` for async assertions
   - Mock external dependencies with `vi.mock()`

3. **Common Test Patterns**
   ```typescript
   // Test async initialization
   await waitFor(() => {
     expect(mockChartInstance.setOption).toHaveBeenCalled();
   });

   // Test state transitions
   const { rerender } = renderWithTheme(<Component {...props} />);
   rerender(<Component {...newProps} />);

   // Test error handling
   expect(onError).toHaveBeenCalledWith(
     expect.objectContaining({ code: 'CHART_INIT_ERROR' })
   );
   ```

4. **Debugging Tests**
   - Use `screen.debug()` to print DOM
   - Use `console.log()` in test for variables
   - Use `--inspect` flag for debugger
   - Check mock call counts with `.mock.calls.length`

## Future Test Enhancements

1. Add E2E tests with Playwright
2. Add visual regression testing
3. Add performance benchmarks
4. Add accessibility audit tests
5. Add snapshot tests for chart options
6. Add tests for memory leaks

## References

- [Vitest Documentation](https://vitest.dev)
- [React Testing Library](https://testing-library.com/react)
- [ECharts API](https://echarts.apache.org/en/api.html)
