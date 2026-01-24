/**
 * Menu Configuration
 * Defines all menu items and their associated components
 */

import { MenuItem } from '../types';
import StockPrices from '../pages/StockPrices';
import Home from '../pages/Home';
import MarketIndex from '../pages/MarketIndex';

/**
 * Available menu items
 * Each item maps to a page/component
 */
export const menuItems: MenuItem[] = [
  {
    id: 'home',
    label: '首页',
    component: Home,
  },
  {
    id: 'market',
    label: '市场',
    children: [
      {
        id: 'market-index',
        label: '大盘',
        component: MarketIndex,
      },
      {
        id: 'stock-individual',
        label: '个股',
        component: StockPrices,
      },
    ],
  },
];

export default menuItems;
