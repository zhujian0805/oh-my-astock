/**
 * Axios API Client Configuration
 * Handles all HTTP communication with the backend API
 * Includes interceptors for logging, error handling, and retry logic
 */

import axios, {
  AxiosInstance,
  AxiosError,
  AxiosRequestConfig,
  InternalAxiosRequestConfig,
} from 'axios';
import { ApiError } from '../types';

/**
 * Maximum number of retry attempts for transient failures
 */
const MAX_RETRIES = 3;

/**
 * Base delay for exponential backoff (ms)
 */
const BASE_DELAY = 1000;

/**
 * HTTP status codes that warrant automatic retry
 */
const RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504];

/**
 * Create and configure Axios instance
 * Uses relative path to leverage Vite proxy in development
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor: Add metadata for debugging
 */
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // Add request timestamp for performance tracking
  (config as any).metadata = { startTime: new Date() };

  if (import.meta.env.VITE_DEBUG) {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
  }

  return config;
});

/**
 * Response Interceptor: Handle errors and implement retry logic
 */
apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.VITE_DEBUG && (response.config as any).metadata) {
      const duration = new Date().getTime() - (response.config as any).metadata.startTime;
      console.log(`[API] Response (${duration}ms): ${response.status}`);
    }
    return response;
  },
  async (error: AxiosError) => {
    const config = error.config as AxiosRequestConfig & { retry?: number };

    // Initialize retry counter
    if (!config.retry) {
      config.retry = 0;
    }

    config.retry += 1;

    // Check if error is retryable
    const shouldRetry =
      RETRYABLE_STATUS_CODES.includes(error.response?.status || 0) &&
      config.retry < MAX_RETRIES;

    if (shouldRetry) {
      // Exponential backoff with jitter
      const delay = BASE_DELAY * Math.pow(2, config.retry - 1);
      const jitter = Math.random() * 0.1 * delay;

      if (import.meta.env.VITE_DEBUG) {
        console.log(
          `[API] Retrying (${config.retry}/${MAX_RETRIES}) after ${delay + jitter}ms`
        );
      }

      await new Promise((resolve) => setTimeout(resolve, delay + jitter));
      return apiClient(config);
    }

    // Process and return error
    const apiError = processError(error);
    return Promise.reject(apiError);
  }
);

/**
 * Process AxiosError and convert to ApiError
 */
function processError(error: AxiosError): ApiError {
  const errorResponse = error.response?.data as any;

  if (errorResponse?.error) {
    // Server returned error in standard format
    return {
      code: errorResponse.error.code || 'UNKNOWN_ERROR',
      message: errorResponse.error.message || 'An unexpected error occurred',
      details: errorResponse.error.details,
      status: error.response?.status,
      timestamp: new Date().toISOString(),
      path: error.config?.url,
    };
  }

  if (error.response) {
    // Server responded with error status
    return {
      code: `HTTP_${error.response.status}`,
      message: errorResponse?.message || `HTTP ${error.response.status}`,
      status: error.response.status,
      timestamp: new Date().toISOString(),
      path: error.config?.url,
    };
  }

  if (error.request) {
    // Request made but no response
    return {
      code: 'NETWORK_ERROR',
      message: 'Network connection failed. Please check your internet connection.',
      status: 0,
      timestamp: new Date().toISOString(),
    };
  }

  // Error in request setup
  return {
    code: 'REQUEST_ERROR',
    message: error.message || 'An unexpected error occurred',
    status: 0,
    timestamp: new Date().toISOString(),
  };
}

export default apiClient;
export { processError };
