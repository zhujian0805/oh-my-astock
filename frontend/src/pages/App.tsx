/**
 * App Component
 * Root application component with Layout, Header, and main content
 */

import React, { useMemo } from 'react';
import Layout from '../components/Layout/Layout';
import Header from '../components/Header/Header';
import ErrorBoundary from '../components/ErrorBoundary';
import { useMenu } from '../hooks/useMenu';
import { menuItems } from '../config/menu';
import { MenuItem } from '../types';

const App: React.FC = () => {
  const { activeMenuId, setActiveMenu, menuItems: items } = useMenu(menuItems);

  // Helper to find item by ID in a nested structure
  const findItem = (items: MenuItem[], id: string): MenuItem | undefined => {
    for (const item of items) {
      if (item.id === id) return item;
      if (item.children) {
        const found = findItem(item.children, id);
        if (found) return found;
      }
    }
    return undefined;
  };

  // Get active component
  const ActiveComponent = useMemo(() => {
    const activeItem = findItem(items, activeMenuId);
    return activeItem?.component || null;
  }, [items, activeMenuId]);

  return (
    <ErrorBoundary>
      <Layout
        header={
          <Header
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
