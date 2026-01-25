/**
 * StockMarketOverviewPage
 * Parent container page for stock market overview with left sidebar
 * Manages submenu navigation (e.g., Shanghai Stock Exchange)
 */

import React, { useState } from 'react';
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
    <div className="flex h-full w-full dark:bg-gray-900 transition-colors duration-200">
      {/* Left Sidebar */}
      <aside className="w-48 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex-shrink-0 flex flex-col transition-colors duration-200">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wide">
            股票市场总貌
          </h2>
        </div>
        <nav className="flex-1 p-2">
          <div className="space-y-1">
            {overviewMenuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveMenuId(item.id)}
                className={`w-full text-left px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeMenuId === item.id
                    ? 'bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden">
        {ActiveComponent ? <ActiveComponent /> : <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">No content</div>}
      </main>
    </div>
  );
};

export default StockMarketOverviewPage;
