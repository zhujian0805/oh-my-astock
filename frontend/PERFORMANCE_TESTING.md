# Performance Testing Guide

This document outlines the testing procedures for Phase 5 performance optimizations (T048-T052).

## Overview

The Stock Market Frontend has been optimized for:
- Large datasets (250-750 data points)
- Responsive design across mobile, tablet, and desktop
- Performance metrics tracking
- Mobile device compatibility

---

## T048: Responsive Design Testing

### Testing Breakpoints

Test the application at three breakpoints:

#### Mobile (320px - md breakpoint)
```bash
# Using Chrome DevTools:
1. Press F12 to open DevTools
2. Click "Toggle device toolbar" (Ctrl+Shift+M)
3. Select "iPhone SE" or set width to 375px
4. Test:
   - Stock selector dropdown displays correctly
   - Chart container fits without overflow
   - X-axis labels are rotated (45°)
   - Y-axis labels are smaller (fontSize: 10px)
   - Statistics grid shows 2 columns
   - Mobile menu button appears
```

#### Tablet (768px - md breakpoint)
```bash
# Using Chrome DevTools:
1. Set width to 768px
2. Test:
   - Sidebar transitions from drawer to fixed position
   - Chart labels are less crowded
   - Statistics grid shows 2 columns (still)
   - All text is readable
```

#### Desktop (1920px)
```bash
# Using Chrome DevTools:
1. Set width to 1920px
2. Test:
   - Full sidebar is visible and fixed
   - Chart has maximum width
   - Statistics grid shows 4 columns
   - All details visible without truncation
```

### Responsive Verification Checklist

- [ ] Mobile (375px): No horizontal scrolling, all elements visible
- [ ] Tablet (768px): Sidebar transitions correctly, chart responsive
- [ ] Desktop (1920px): Full layout with sidebar, no wasted space
- [ ] Font sizes scale appropriately at each breakpoint
- [ ] Touch targets are at least 44x44px on mobile
- [ ] No text truncation on mobile
- [ ] Chart axis labels don't overlap on mobile

---

## T049: Performance Testing (Large Datasets)

### Setup

1. Select a stock with 1+ years of historical data (e.g., "000001 - Ping An Bank")
2. Ensure the application is running in production mode:
   ```bash
   npm run build
   npm run preview
   ```

### Test Metrics

#### Render Time Measurement

Use Chrome DevTools Performance tab:

```
1. Open DevTools (F12)
2. Go to Performance tab
3. Click record (or Ctrl+Shift+E)
4. Select a stock with 750+ data points
5. Wait for chart to render
6. Stop recording
7. Review metrics:
   - Scripting time (should be < 500ms)
   - Rendering time (should be < 500ms)
   - Total time from click to chart visible (should be < 2s)
```

**Expected Performance**:
- 250 points: < 800ms
- 500 points: < 1200ms
- 750 points: < 1800ms

#### Interaction Performance

Test hover and tooltip interactions:

```
1. After chart renders, move mouse over chart
2. Observe tooltip appearance
3. Time the response: Should be < 100ms
4. Try zooming/panning if enabled
5. Monitor FPS in DevTools (should stay > 50 FPS)
```

#### Memory Usage

Monitor in DevTools Memory tab:

```
1. Take heap snapshot before loading data
2. Load stock with 750+ data points
3. Take heap snapshot after
4. Compare: Should not exceed 50MB additional
5. Select different stocks 5 times
6. Take final snapshot: Should not continuously grow
```

### Performance Testing Checklist

- [ ] 250 points render in < 800ms
- [ ] 500 points render in < 1200ms
- [ ] 750 points render in < 1800ms
- [ ] Tooltip responds within 100ms
- [ ] FPS stays > 50 during interactions
- [ ] Memory does not continuously grow
- [ ] Canvas renderer is being used (not SVG)
- [ ] No JavaScript errors in console

---

## T050: Lazy Loading Implementation

### Current Implementation

Stock list uses lazy loading through:
- Pagination in API (if supported by backend)
- Client-side filtering via useMemo
- Virtualization not yet implemented

### Testing Lazy Loading

```bash
# 1. Monitor network tab in DevTools
# 2. Open stock selector
# 3. Verify:
#    - Only initial set of stocks loaded
#    - Remaining stocks loaded on scroll (if implemented)
#    - No redundant API calls
```

### Future Enhancement

For very large stock lists (10,000+), consider:
- Virtual scrolling (react-window or similar)
- Pagination with "Load More" button
- Search-based filtering before display

---

## T051: Loading State Indication

### Current Implementation

Loading states are shown via:
- `LoadingSpinner` component during data fetch
- Message: "Loading chart data..."
- Appears while `isLoading = true`

### Testing Loading State

```bash
# 1. Open application
# 2. Select a stock
# 3. Observe LoadingSpinner appears immediately
# 4. Wait for chart to load
# 5. Verify spinner disappears when chart renders
# 6. Check console for performance metrics (in dev mode)
```

### Console Output (Development Mode)

When `NODE_ENV === 'development'`, you should see:

```
[Chart Performance] Rendered 500 data points in 1234.56ms {
  dataPoints: 500,
  duration: "1234.56ms",
  pointsPerMs: "0.41"
}
```

---

## T052: Mobile Device Testing

### iOS (Safari)

```bash
# Method 1: Simulator
1. Open Xcode
2. Devices & Simulators → iPhone simulator
3. Safari → Preferences → Advanced → Enable Web Inspector
4. Connect device to development machine
5. Open website in Safari on simulator
6. Inspect in Safari desktop

# Method 2: Real Device
1. On iPhone: Settings → Safari → Advanced → Web Inspector (ON)
2. Connect via USB to Mac
3. In Safari on Mac: Develop → [Device] → Select page to inspect
```

### Android (Chrome)

```bash
# Method 1: Emulator
1. Android Studio → Virtual Device Manager
2. Create/launch emulator
3. In Chrome: chrome://inspect/#devices
4. Select device and page

# Method 2: Real Device
1. Enable USB debugging on device
2. Connect via USB to computer
3. In Chrome: chrome://inspect/#devices
4. Tap "Inspect" to open DevTools
```

### Mobile Testing Checklist

- [ ] Chart renders on iOS Safari
- [ ] Chart renders on Android Chrome
- [ ] Touch interactions work (no mouse hover needed)
- [ ] Landscape mode works (chart reflows)
- [ ] Portrait mode works (chart is readable)
- [ ] No JavaScript errors in console
- [ ] Network requests succeed (check Network tab)
- [ ] Performance acceptable on 4G LTE (not WiFi)
- [ ] Battery usage is reasonable (DevTools → Battery)

---

## T043-T046: Optimization Verification

These have been implemented. Verify the optimizations:

### T043: ECharts Configuration

Check `/frontend/src/utils/charts.ts`:
- ✅ Canvas renderer with `useDirtyRect: true`
- ✅ No animations (`animation: false`)
- ✅ LTTB sampling for datasets > 500 points
- ✅ No symbols on line (`symbol: 'none'`)
- ✅ Smooth curves only for small datasets
- ✅ Data validation function

### T044: Responsive Chart Options

Check `/frontend/src/components/StockChart/StockChart.tsx`:
- ✅ Mobile detection (`window.innerWidth < 768`)
- ✅ Responsive grid margins
- ✅ Reduced labels on mobile
- ✅ Responsive axis label intervals
- ✅ Debounced resize handler (300ms)

### T045: React.memo Wrappers

Check exports:
- ✅ `/frontend/src/components/StockChart/StockChart.tsx`: `export default React.memo(StockChart)`
- ✅ `/frontend/src/components/StockSelector/StockSelector.tsx`: `export default React.memo(StockSelector)`

### T046: useMemo Optimizations

Check `/frontend/src/components/StockChart/StockChart.tsx`:
- ✅ `const stats = useMemo(() => getChartStatistics(chartData), [chartData])`
- ✅ Statistics calculation memoized to prevent recalculation

---

## Running Automated Performance Tests

### Using Lighthouse

```bash
1. Open DevTools (F12)
2. Go to Lighthouse tab
3. Select "Performance" + "Accessibility"
4. Click "Analyze page load"
5. Review metrics:
   - First Contentful Paint (FCP): < 1.5s
   - Largest Contentful Paint (LCP): < 2.5s
   - Cumulative Layout Shift (CLS): < 0.1
   - Time to Interactive (TTI): < 3.8s
```

### Using WebPageTest

```bash
1. Visit https://www.webpagetest.org/
2. Enter: http://localhost:5173
3. Select location and browser
4. Run test
5. Compare with baseline
```

---

## Performance Optimization Tips

### For Users

1. Use latest browser version (Chrome 90+, Safari 15+, Firefox 88+)
2. Close unnecessary browser tabs
3. Use desktop for large dataset testing (better performance)
4. On mobile, close other apps and enable low-power mode is OFF

### For Developers

1. Profile early and often using DevTools
2. Use `npm run build` before performance testing (dev mode is slower)
3. Disable browser extensions during testing (can affect performance)
4. Test on both fast and slow networks (DevTools → Network throttling)
5. Monitor Core Web Vitals continuously

---

## Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Chart render (750 points) | < 2 seconds | ✅ Implemented |
| Responsive mobile (320px) | No overflow | ✅ Implemented |
| Responsive tablet (768px) | No overflow | ✅ Implemented |
| Responsive desktop (1920px) | Full layout | ✅ Implemented |
| Interaction response | < 100ms | ✅ Optimized |
| Memory usage | < 50MB | ✅ Optimized |
| iOS Safari compatibility | Works | ⏳ Test needed |
| Android Chrome compatibility | Works | ⏳ Test needed |

---

## Troubleshooting

### Chart Not Rendering

**Symptom**: Chart container appears empty

**Solution**:
1. Check browser console for errors (F12)
2. Verify ECharts library loaded: `window.echarts` in console
3. Check Network tab for failed requests
4. Verify stock data is available via API

### Performance Issues on Mobile

**Symptom**: Chart rendering takes > 5 seconds

**Solution**:
1. Reduce dataset size (request last 6 months instead of 1 year)
2. Verify 4G/LTE connection (not WiFi for throttling test)
3. Close background apps
4. Check for JavaScript errors (F12 Console tab)
5. Use Canvas renderer (not SVG)

### Tooltip Not Appearing

**Symptom**: Hover over chart shows nothing

**Solution**:
1. Check mouse position is over chart area
2. Verify tooltip configuration in `getChartOption`
3. Test in Chrome first (most compatible)
4. Check z-index conflicts with other elements

---

## Next Steps

After completing T048-T052:

1. Merge Phase 5 optimizations to `main` branch
2. Deploy to staging environment
3. Collect real-world performance metrics
4. Gather user feedback on responsiveness
5. Plan Phase N (Polish) enhancements
6. Consider implementing virtual scrolling for 10,000+ stocks

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-23
**Phase**: 5 (Performance Optimization)
