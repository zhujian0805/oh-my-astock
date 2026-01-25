/**
 * MenuItem Component
 * Individual menu item with active state styling
 * Supports nested child menu items
 */

import React, { useState } from 'react';
import { MenuItemProps } from '../../types';

const MenuItem: React.FC<MenuItemProps> = ({ item, isActive, onClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const hasChildren = item.children && item.children.length > 0;

  const handleClick = () => {
    if (hasChildren) {
      setIsExpanded(!isExpanded);
    } else {
      onClick();
    }
  };

  return (
    <div>
      <button
        onClick={handleClick}
        className={`w-full flex items-center gap-4 px-4 py-2 text-left rounded-r-full mr-2 transition-colors ${
          isActive
            ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
        }`}
      >
        {item.icon && <span className="text-xl">{item.icon}</span>}
        <span className="font-medium text-sm tracking-wide flex-1">{item.label}</span>
        {hasChildren && (
          <span className={`text-xs transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
            ▼
          </span>
        )}
      </button>

      {/* Nested Children */}
      {hasChildren && isExpanded && (
        <div className="pl-4 space-y-1 mt-1">
          {(item.children || []).map((child) => (
            <MenuItem
              key={child.id}
              item={child}
              isActive={isActive}
              onClick={() => onClick()}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default MenuItem;
