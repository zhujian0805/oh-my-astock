/**
 * Formatter Utility Functions
 * Handles date, number, and currency formatting
 */

/**
 * Format date string to YYYY-MM-DD format
 */
export function formatDate(date: string | Date, format: 'YYYY-MM-DD' | 'YYYY/MM/DD' = 'YYYY-MM-DD'): string {
  const d = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(d.getTime())) {
    return '';
  }

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');

  if (format === 'YYYY-MM-DD') {
    return `${year}-${month}-${day}`;
  }

  return `${year}/${month}/${day}`;
}

/**
 * Format price to 2 decimal places with optional currency symbol
 */
export function formatPrice(price: number, currency: string = '¥', decimals: number = 2): string {
  if (typeof price !== 'number' || isNaN(price)) {
    return '-';
  }

  const formatted = price.toFixed(decimals);
  return `${currency}${formatted}`;
}

/**
 * Format large numbers with thousand separators
 */
export function formatNumber(num: number, decimals: number = 0): string {
  if (typeof num !== 'number' || isNaN(num)) {
    return '-';
  }

  return num.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format volume with units (K for thousand, M for million, B for billion)
 */
export function formatVolume(volume: number): string {
  if (volume >= 1e9) {
    return `${(volume / 1e9).toFixed(2)}B`;
  }

  if (volume >= 1e6) {
    return `${(volume / 1e6).toFixed(2)}M`;
  }

  if (volume >= 1e3) {
    return `${(volume / 1e3).toFixed(2)}K`;
  }

  return volume.toString();
}

/**
 * Format percentage with color indication
 */
export function formatPercent(value: number, decimals: number = 2): string {
  if (typeof value !== 'number' || isNaN(value)) {
    return '-';
  }

  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(decimals)}%`;
}

export default {
  formatDate,
  formatPrice,
  formatNumber,
  formatVolume,
  formatPercent,
};
