/**
 * StockMarketOverviewPage
 * Parent container page for stock market overview with left sidebar
 * Manages submenu navigation (e.g., Shanghai Stock Exchange)
 */

import React, { useState } from 'react';
import './StockMarketOverviewPage.css';
import StockMarketOverview from './StockMarketOverview';

interface OverviewMenuItem {
  id: string;
  label: string;
  component: React.ComponentType<any>;
}

const overviewMenuItems: OverviewMenuItem[] = [
  {
    id: 'sse-summary',
    label: '上海证券交易所',
    component: StockMarketOverview,
  },
];

const StockMarketOverviewPage: React.FC = () => {
  const [activeMenuId, setActiveMenuId] = useState<string>('sse-summary');

  const activeItem = overviewMenuItems.find(item => item.id === activeMenuId);
  const ActiveComponent = activeItem?.component || null;

  return (
    <div className="stock-market-overview-page">
      {/* Left Sidebar */}
      <aside className="overview-sidebar">
        <h2 className="sidebar-title">股票市场总貌</h2>
        <nav className="sidebar-menu">
          {overviewMenuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveMenuId(item.id)}
              className={`sidebar-menu-item ${
                activeMenuId === item.id ? 'active' : ''
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="overview-content">
        {ActiveComponent ? <ActiveComponent /> : <div>No content</div>}
      </main>
    </div>
  );
};

export default StockMarketOverviewPage;
