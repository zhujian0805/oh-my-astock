/**
 * Menu Configuration
 * Defines all menu items and their associated components
 */

import { MenuItem } from '../types';
import StockPrices from '../pages/StockPrices';
import StockMarketOverviewPage from '../pages/StockMarketOverviewPage';
import Home from '../pages/Home';
import IndividualStockPage from '../pages/IndividualStockPage';

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
    label: '股市数据',
    children: [
      {
        id: 'market-overview',
        label: '股票市场总貌',
        component: StockMarketOverviewPage,
      },
      {
        id: 'stock-prices',
        label: '历史行情数据',
        component: StockPrices,
      },
      {
        id: 'stock-individual',
        label: '个股信息',
        component: IndividualStockPage,
      },
    ],
  },
];

export default menuItems;
