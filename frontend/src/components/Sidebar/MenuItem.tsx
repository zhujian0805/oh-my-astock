/**
 * MenuItem Component
 * Individual menu item with active state styling
 */

import React from 'react';
import { MenuItemProps } from '../../types';

const MenuItem: React.FC<MenuItemProps> = ({ item, isActive, onClick }) => {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-4 px-4 py-2 text-left rounded-r-full mr-2 transition-colors ${
        isActive
          ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
      }`}
    >
      {item.icon && <span className="text-xl material-icons-outlined">{item.icon}</span>}
      <span className="font-medium text-sm tracking-wide">{item.label}</span>
    </button>
  );
};

export default MenuItem;
