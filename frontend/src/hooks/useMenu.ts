/**
 * useMenu Hook
 * Manages active menu item state and persistence
 */

import { useState, useCallback, useEffect } from 'react';
import { MenuItem, UseMenuReturn } from '../types';

const MENU_STATE_KEY = 'app:activeMenuId';
const DEFAULT_MENU_ID = 'stock-prices';

/**
 * Custom hook to manage menu state
 */
export function useMenu(items: MenuItem[]): UseMenuReturn {
  // Initialize from sessionStorage if available
  const [activeMenuId, setActiveMenuIdState] = useState<string>(() => {
    if (typeof window === 'undefined') {
      return DEFAULT_MENU_ID;
    }
    return sessionStorage.getItem(MENU_STATE_KEY) || DEFAULT_MENU_ID;
  });

  // Validate that active menu ID exists in items
  const isValidMenuId = items.some((item) => item.id === activeMenuId);
  const currentActiveId = isValidMenuId ? activeMenuId : DEFAULT_MENU_ID;

  // Set active menu and persist to sessionStorage
  const setActiveMenu = useCallback(
    (id: string) => {
      // Validate menu ID exists
      if (items.some((item) => item.id === id)) {
        setActiveMenuIdState(id);
        sessionStorage.setItem(MENU_STATE_KEY, id);
      }
    },
    [items]
  );

  // Sync state to sessionStorage on change
  useEffect(() => {
    sessionStorage.setItem(MENU_STATE_KEY, currentActiveId);
  }, [currentActiveId]);

  return {
    activeMenuId: currentActiveId,
    setActiveMenu,
    menuItems: items,
  };
}

export default useMenu;
