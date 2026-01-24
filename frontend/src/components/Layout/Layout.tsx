/**
 * Layout Component
 * Main layout with sidebar and content pane
 * Responsive: stacked on mobile, side-by-side on tablet+
 */

import React from 'react';
import { LayoutProps } from '../../types';

const Layout: React.FC<LayoutProps> = ({ children, sidebar }) => {
  return (
    <div className="flex flex-col md:flex-row h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Sidebar - Full width on mobile, fixed width on tablet+ */}
      {sidebar && (
        <aside className="w-full md:w-56 bg-white dark:bg-gray-800 shadow-[4px_0_24px_rgba(0,0,0,0.02)] dark:border-r dark:border-gray-700 z-10 flex-shrink-0 transition-colors duration-200">
          {sidebar}
        </aside>
      )}

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto">
        <div className="w-full h-full p-2 text-gray-900 dark:text-gray-100">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
