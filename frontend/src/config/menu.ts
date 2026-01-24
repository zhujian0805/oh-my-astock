/**
 * Menu Configuration
 * Defines all sidebar menu items and their associated components
 */

import { MenuItem } from '../types';
import StockPrices from '../pages/StockPrices';

/**
 * Available menu items
 * Each item maps to a page/component
 */
export const menuItems: MenuItem[] = [
  {
    id: 'stock-prices',
    label: 'Stock Prices',
    icon: '📈',
    component: StockPrices,
  },
  // Future menu items can be added here:
  // {
  //   id: 'stock-comparison',
  //   label: 'Stock Comparison',
  //   icon: '⚖️',
  //   component: StockComparison,
  // },
  // {
  //   id: 'market-analysis',
  //   label: 'Market Analysis',
  //   icon: '📊',
  //   component: MarketAnalysis,
  // },
];

export default menuItems;
