/**
 * Stock Info Dropdown Component
 * Dropdown for selecting stock codes to display individual information
 */

import React from 'react';

interface StockInfoDropdownProps {
  value: string;
  onChange: (stockCode: string) => void;
  disabled?: boolean;
  className?: string;
}

// Example stock codes - in production this would come from an API
const EXAMPLE_STOCKS = [
  { code: '000001', name: '平安银行' },
  { code: '000002', name: '万科A' },
  { code: '600000', name: '浦发银行' },
  { code: '600036', name: '招商银行' },
  { code: '000858', name: '五粮液' },
  { code: '600519', name: '贵州茅台' },
];

const StockInfoDropdown: React.FC<StockInfoDropdownProps> = ({
  value,
  onChange,
  disabled = false,
  className = '',
}) => {
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(event.target.value);
  };

  return (
    <div className={`flex flex-col space-y-2 ${className}`}>
      <label htmlFor="stock-select" className="text-sm font-medium text-gray-700">
        选择股票代码
      </label>
      <select
        id="stock-select"
        value={value}
        onChange={handleChange}
        disabled={disabled}
        className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
      >
        <option value="">请选择股票...</option>
        {EXAMPLE_STOCKS.map((stock) => (
          <option key={stock.code} value={stock.code}>
            {stock.code} - {stock.name}
          </option>
        ))}
      </select>
      <p className="text-xs text-gray-500">
        选择股票代码查看详细信息
      </p>
    </div>
  );
};

export default StockInfoDropdown;