/**
 * ErrorMessage Component
 * Displays error message with optional retry button
 */

import React from 'react';
import { ErrorMessageProps } from '../../types';
import { getErrorMessage } from '../../utils/errors';

const ErrorMessage: React.FC<ErrorMessageProps> = ({ error, onRetry }) => {
  const message = getErrorMessage(error);

  return (
    <div className="flex flex-col items-center justify-center py-8 px-4">
      <div className="max-w-md w-full p-6 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg
              className="h-6 w-6 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-900">Error</h3>
            <div className="mt-2 text-sm text-red-700">{message}</div>
            {onRetry && (
              <div className="mt-4">
                <button
                  onClick={onRetry}
                  className="inline-flex items-center px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;
