"""Debug utilities for development and testing."""

import functools
import time
from typing import Any, Callable, TypeVar
from lib.logging import get_logger

logger = get_logger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def debug_metrics(func: F) -> F:
    """Decorator to log function execution metrics."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {e}")
            raise
    return wrapper  # type: ignore


def timed_operation(operation_name_or_func):
    """Decorator or context manager for timing operations."""
    if callable(operation_name_or_func):
        # Used as @timed_operation (without parentheses)
        func = operation_name_or_func
        operation_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.debug(f"Operation '{operation_name}' completed in {execution_time:.4f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Operation '{operation_name}' failed after {execution_time:.4f}s: {e}")
                raise
        return wrapper
    else:
        # Used as @timed_operation("name") - return a decorator
        operation_name = operation_name_or_func

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    logger.debug(f"Operation '{operation_name}' completed in {execution_time:.4f}s")
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"Operation '{operation_name}' failed after {execution_time:.4f}s: {e}")
                    raise
            return wrapper
        return decorator


def debug_context(context_name: str, **context_data):
    """Context manager for debug logging with context data."""
    class DebugContext:
        def __enter__(self):
            logger.debug(f"Entering context: {context_name}", extra=context_data)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                logger.error(f"Context '{context_name}' failed: {exc_val}", extra=context_data)
            else:
                logger.debug(f"Exiting context: {context_name}", extra=context_data)

    return DebugContext()


def log_data_validation(data: Any, validation_result: bool, context: str = ""):
    """Log data validation results."""
    if validation_result:
        logger.debug(f"Data validation passed for {context}: {type(data).__name__}")
    else:
        logger.warning(f"Data validation failed for {context}: {type(data).__name__}")