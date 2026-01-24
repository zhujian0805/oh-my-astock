/**
 * App Component
 * Root application component with Layout, Sidebar, and main content
 */

import React, { useMemo } from 'react';
import Layout from '../components/Layout/Layout';
import Sidebar from '../components/Sidebar/Sidebar';
import ErrorBoundary from '../components/ErrorBoundary';
import { useMenu } from '../hooks/useMenu';
import { menuItems } from '../config/menu';

const App: React.FC = () => {
  const { activeMenuId, setActiveMenu, menuItems: items } = useMenu(menuItems);

  // Get active component
  const ActiveComponent = useMemo(() => {
    const activeItem = items.find((item) => item.id === activeMenuId);
    return activeItem?.component || null;
  }, [items, activeMenuId]);

  return (
    <ErrorBoundary>
      <Layout
        sidebar={
          <Sidebar
            items={items}
            activeId={activeMenuId}
            onSelect={setActiveMenu}
          />
        }
      >
        {ActiveComponent ? <ActiveComponent /> : <div>No content</div>}
      </Layout>
    </ErrorBoundary>
  );
};

export default App;
