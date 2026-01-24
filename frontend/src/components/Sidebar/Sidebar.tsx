/**
 * Sidebar Component
 * Navigation sidebar with menu items
 * Responsive: full-width on mobile, fixed sidebar on tablet+
 */

import React, { useState } from 'react';
import { SidebarProps } from '../../types';
import MenuItem from './MenuItem';
import ThemeToggle from '../common/ThemeToggle';
import { useTheme } from '../../contexts/ThemeContext';

const Sidebar: React.FC<SidebarProps> = ({
  items,
  activeId,
  onSelect,
  isOpen = true,
  onClose,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSelectItem = (id: string) => {
    onSelect(id);
    setMobileMenuOpen(false);
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <div className="md:hidden p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between bg-white dark:bg-gray-800">
        <h1 className="text-lg font-bold text-gray-900 dark:text-white">Stock Market</h1>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-gray-600 dark:text-gray-300"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/50 md:hidden z-20"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Menu Items Container */}
      <div
        className={`${
          mobileMenuOpen ? 'block' : 'hidden'
        } md:flex md:flex-col md:h-full py-2 space-y-1`}
      >
        {/* Header */}
        <div className="hidden md:flex px-4 mb-4 mt-2 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center text-white font-bold">
              S
            </div>
            <h1 className="text-lg font-normal text-gray-600 dark:text-gray-300">Stock Market</h1>
          </div>
          <ThemeToggle />
        </div>

        {/* Menu Items */}
        <nav className="pr-2 flex-1 overflow-y-auto">
          {items.map((item) => (
            <MenuItem
              key={item.id}
              item={item}
              isActive={activeId === item.id}
              onClick={() => handleSelectItem(item.id)}
            />
          ))}
        </nav>

        {/* Footer */}
        <div className="px-6 pt-4 mt-8 border-t border-gray-100 mx-4">
          <p className="text-xs text-gray-500">
            Version 0.1.0
          </p>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
