/**
 * Layout Component
 * Main layout with header and content pane
 */

import React from 'react';
import { LayoutProps } from '../../types';

const Layout: React.FC<LayoutProps> = ({ children, header }) => {
  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Header - Fixed at top */}
      {header && (
        <div className="flex-shrink-0 w-full z-20">
          {header}
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden relative flex flex-col">
        <div className="w-full h-full p-4 text-gray-900 dark:text-gray-100 overflow-y-auto flex flex-col">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
