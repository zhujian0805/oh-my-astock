/**
 * MonthPicker Component
 * A compact month picker dropdown similar to DatePicker styling
 */

import React, { useState, useRef } from 'react';

interface MonthPickerProps {
  selectedMonth: { year: number; month: number } | null;
  onMonthSelect: (month: { year: number; month: number }) => void;
  className?: string;
}

const MonthPicker: React.FC<MonthPickerProps> = ({
  selectedMonth,
  onMonthSelect,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [viewYear, setViewYear] = useState(selectedMonth?.year || new Date().getFullYear());
  const pickerRef = useRef<HTMLDivElement>(null);

  const months = [
    '01', '02', '03', '04', '05', '06',
    '07', '08', '09', '10', '11', '12'
  ];

  const monthNames = [
    '一月', '二月', '三月', '四月', '五月', '六月',
    '七月', '八月', '九月', '十月', '十一月', '十二月'
  ];

  const handleMonthClick = (monthIndex: number) => {
    onMonthSelect({ year: viewYear, month: monthIndex + 1 });
    setIsOpen(false);
  };

  const togglePicker = () => {
    setIsOpen(!isOpen);
  };

  const goToPreviousYear = () => {
    if (viewYear > 2020) {
      setViewYear(viewYear - 1);
    }
  };

  const goToNextYear = () => {
    if (viewYear < 2030) {
      setViewYear(viewYear + 1);
    }
  };

  const isMonthSelected = (monthIndex: number) => {
    return selectedMonth &&
           selectedMonth.year === viewYear &&
           selectedMonth.month === monthIndex + 1;
  };

  const isCurrentMonth = (monthIndex: number) => {
    const now = new Date();
    return viewYear === now.getFullYear() && monthIndex === now.getMonth();
  };

  // Close picker when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Update view year when selected month changes
  React.useEffect(() => {
    if (selectedMonth) {
      setViewYear(selectedMonth.year);
    }
  }, [selectedMonth]);

  const displayValue = selectedMonth
    ? `${selectedMonth.year}-${selectedMonth.month.toString().padStart(2, '0')}`
    : '选择月份';

  return (
    <div className={`relative ${className}`} ref={pickerRef}>
      {/* Input Field */}
      <div className="flex flex-col z-20 relative">
        <label className="text-[10px] text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide mb-0.5">
          选择月份
        </label>
        <button
          onClick={togglePicker}
          className="w-full px-2 py-1.5 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-primary-500 text-left"
          type="button"
        >
          {displayValue}
        </button>
      </div>

      {/* Dropdown Calendar */}
      {isOpen && (
        <div className="absolute top-full right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded shadow-lg z-50 w-64 max-h-80 overflow-hidden">
          {/* Year Navigation */}
          <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-600">
            <button
              onClick={goToPreviousYear}
              disabled={viewYear <= 2020}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              type="button"
            >
              ‹
            </button>
            <span className="text-sm font-semibold text-gray-900 dark:text-white">
              {viewYear}年
            </span>
            <button
              onClick={goToNextYear}
              disabled={viewYear >= 2030}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              type="button"
            >
              ›
            </button>
          </div>

          {/* Month Grid */}
          <div className="p-3 max-h-48 overflow-y-auto">
            <div className="grid grid-cols-3 gap-1">
              {monthNames.map((monthName, index) => (
                <button
                  key={index}
                  onClick={() => handleMonthClick(index)}
                  className={`p-2 text-xs rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors ${
                    isMonthSelected(index)
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : isCurrentMonth(index)
                      ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                      : 'text-gray-700 dark:text-gray-300'
                  }`}
                  type="button"
                >
                  {monthName}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MonthPicker;