/**
 * Error Handling Utilities
 * Converts technical errors to user-friendly messages
 */

import { ApiError } from '../types';

/**
 * Map error codes to user-friendly messages
 */
const ERROR_MESSAGES: Record<string, string> = {
  NETWORK_ERROR: 'Network connection failed. Please check your internet connection and try again.',
  REQUEST_ERROR: 'Failed to process request. Please try again.',
  TIMEOUT_ERROR: 'Request timed out. The server took too long to respond.',
  NOT_FOUND: 'The requested resource was not found.',
  INVALID_REQUEST: 'Invalid request. Please check your input.',
  INVALID_DATE_RANGE: 'Invalid date range. End date must be after start date.',
  RATE_LIMIT_EXCEEDED: 'Too many requests. Please wait a moment before trying again.',
  SERVER_ERROR: 'Server error. The service is temporarily unavailable.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again later.',
};

/**
 * Get user-friendly error message from ApiError
 */
export function getErrorMessage(error: ApiError | string | null): string {
  if (!error) {
    return ERROR_MESSAGES.UNKNOWN_ERROR;
  }

  if (typeof error === 'string') {
    return error;
  }

  // Check if there's a custom message in ERROR_MESSAGES
  if (error.code && ERROR_MESSAGES[error.code]) {
    return ERROR_MESSAGES[error.code];
  }

  // Use message from error object
  if (error.message) {
    return error.message;
  }

  // Map HTTP status codes
  if (error.status) {
    return mapStatusCodeToMessage(error.status);
  }

  return ERROR_MESSAGES.UNKNOWN_ERROR;
}

/**
 * Map HTTP status code to user-friendly message
 */
function mapStatusCodeToMessage(status: number): string {
  const statusMessages: Record<number, string> = {
    400: 'Bad request. Please check your input.',
    401: 'Unauthorized. Please log in.',
    403: 'You do not have permission to access this resource.',
    404: 'The requested resource was not found.',
    408: 'Request timeout. Please try again.',
    429: 'Too many requests. Please wait a moment.',
    500: 'Server error. Please try again later.',
    502: 'Bad gateway. The service is temporarily unavailable.',
    503: 'Service unavailable. Please try again later.',
    504: 'Gateway timeout. The service is temporarily unavailable.',
  };

  return statusMessages[status] || ERROR_MESSAGES.SERVER_ERROR;
}

/**
 * Check if error is network-related
 */
export function isNetworkError(error: ApiError): boolean {
  return (
    error.code === 'NETWORK_ERROR' ||
    error.code === 'REQUEST_ERROR' ||
    error.code === 'TIMEOUT_ERROR' ||
    (error.status && error.status >= 500 && error.status < 600) ||
    error.status === 0
  );
}

/**
 * Check if error is transient (retryable)
 */
export function isTransientError(error: ApiError): boolean {
  const transientCodes = ['TIMEOUT_ERROR', 'NETWORK_ERROR', 'RATE_LIMIT_EXCEEDED'];
  const transientStatuses = [408, 429, 500, 502, 503, 504];

  return (
    transientCodes.includes(error.code) ||
    (error.status !== undefined && transientStatuses.includes(error.status))
  );
}

/**
 * Create a standardized error object
 */
export function createError(
  code: string,
  message: string,
  details?: Record<string, any>
): ApiError {
  return {
    code,
    message,
    details,
    timestamp: new Date().toISOString(),
  };
}

export default {
  getErrorMessage,
  mapStatusCodeToMessage,
  isNetworkError,
  isTransientError,
  createError,
};
