"""Retry and backoff utilities for robust API operations.

Implements exponential backoff with jitter, exponential backoff with optional
circuit breaker for network failures.
"""

import random
import time
from functools import wraps
from typing import Callable, Optional, Type, TypeVar, Union
from collections.abc import Sequence


T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 5,
        initial_backoff: float = 1.0,
        max_backoff: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        calm_down_time: float = 0.5,
    ):
        """Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            initial_backoff: Initial backoff duration in seconds
            max_backoff: Maximum backoff duration in seconds
            backoff_multiplier: Multiplier for exponential backoff
            jitter: Whether to add random jitter to backoff
            calm_down_time: Additional calm-down duration before each retry in seconds
        """
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.calm_down_time = calm_down_time

    def calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff duration for the given attempt.

        Args:
            attempt: Zero-indexed attempt number

        Returns:
            Backoff duration in seconds
        """
        backoff = min(
            self.initial_backoff * (self.backoff_multiplier ** attempt),
            self.max_backoff,
        )

        if self.jitter:
            # Add random jitter: ±20% of backoff
            jitter_amount = backoff * 0.2 * (random.random() * 2 - 1)
            backoff = max(0, backoff + jitter_amount)

        # Add calm-down time on top of backoff
        total_wait = backoff + self.calm_down_time
        return total_wait


def retry(
    exceptions: Union[Type[Exception], Sequence[Type[Exception]]] = Exception,
    config: Optional[RetryConfig] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying a function with exponential backoff.

    Args:
        exceptions: Exception type(s) to catch and retry on
        config: RetryConfig instance, defaults to sensible defaults

    Returns:
        Decorated function that will retry on specified exceptions

    Example:
        @retry(exceptions=requests.RequestException)
        def fetch_data():
            return requests.get('https://api.example.com/data')
    """
    if config is None:
        config = RetryConfig()

    if isinstance(exceptions, type):
        exceptions = (exceptions,)
    else:
        exceptions = tuple(exceptions)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < config.max_retries - 1:
                        backoff = config.calculate_backoff(attempt)
                        time.sleep(backoff)

            # All retries exhausted
            raise last_exception

        return wrapper

    return decorator


def retry_with_logger(
    exceptions: Union[Type[Exception], Sequence[Type[Exception]]] = Exception,
    config: Optional[RetryConfig] = None,
    logger: Optional[object] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying a function with logging.

    Args:
        exceptions: Exception type(s) to catch and retry on
        config: RetryConfig instance
        logger: Logger instance (optional)

    Returns:
        Decorated function that logs retry attempts
    """
    if config is None:
        config = RetryConfig()

    if isinstance(exceptions, type):
        exceptions = (exceptions,)
    else:
        exceptions = tuple(exceptions)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < config.max_retries - 1:
                        backoff = config.calculate_backoff(attempt)
                        if logger:
                            logger.warning(
                                f"Function {func.__name__} failed (attempt {attempt + 1}/{config.max_retries}): {e}. "
                                f"Retrying in {backoff:.1f} seconds..."
                            )
                        time.sleep(backoff)
                    else:
                        if logger:
                            logger.error(
                                f"Function {func.__name__} failed after {config.max_retries} attempts: {e}"
                            )

            raise last_exception

        return wrapper

    return decorator
