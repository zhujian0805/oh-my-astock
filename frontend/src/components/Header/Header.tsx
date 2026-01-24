import React, { useState } from 'react';
import { MenuItem } from '../../types';

interface HeaderProps {
  items: MenuItem[];
  activeId: string;
  onSelect: (id: string) => void;
}

const Header: React.FC<HeaderProps> = ({ items, activeId, onSelect }) => {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-md h-16 flex items-center px-6 z-50 relative shrink-0">
      <div className="text-xl font-bold mr-10 text-gray-900 dark:text-white flex items-center">
        Oh My Astock
      </div>
      <nav className="flex space-x-2 h-full items-center">
        {items.map((item) => (
          <NavMenuItem
            key={item.id}
            item={item}
            activeId={activeId}
            onSelect={onSelect}
          />
        ))}
      </nav>
    </header>
  );
};

const NavMenuItem: React.FC<{
  item: MenuItem;
  activeId: string;
  onSelect: (id: string) => void;
}> = ({ item, activeId, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  // Check if this item or any of its children is active
  const isActive = item.id === activeId || item.children?.some(child => child.id === activeId);

  if (item.children) {
    return (
      <div 
        className="relative h-full flex items-center"
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
      >
        <button
          className={`px-3 py-2 rounded-md transition-colors font-medium ${
            isActive 
              ? 'text-blue-600 dark:text-blue-400' 
              : 'text-gray-700 hover:text-blue-600 dark:text-gray-200 dark:hover:text-blue-400'
          }`}
        >
          {item.label}
        </button>
        {isOpen && (
          <div className="absolute top-[80%] left-0 w-48 bg-white dark:bg-gray-800 shadow-xl rounded-md py-1 border border-gray-100 dark:border-gray-700">
            {item.children.map((child) => (
              <button
                key={child.id}
                onClick={() => {
                  onSelect(child.id);
                  setIsOpen(false);
                }}
                className={`block w-full text-left px-4 py-2 text-sm transition-colors ${
                  child.id === activeId
                    ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                    : 'text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700'
                }`}
              >
                {child.label}
              </button>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <button
      onClick={() => onSelect(item.id)}
      className={`px-3 py-2 rounded-md transition-colors font-medium ${
        item.id === activeId
          ? 'text-blue-600 dark:text-blue-400'
          : 'text-gray-700 hover:text-blue-600 dark:text-gray-200 dark:hover:text-blue-400'
      }`}
    >
      {item.label}
    </button>
  );
};

export default Header;
