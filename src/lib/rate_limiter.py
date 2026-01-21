"""Rate limiting utilities for API requests.

Implements token bucket and fixed-rate throttling to prevent API rate limiting
and excessive resource consumption.
"""

import time
from threading import Lock
from typing import Optional


class RateLimiter:
    """Fixed-rate throttling using token bucket algorithm.

    Ensures requests are spaced at least min_interval apart to prevent
    overwhelming APIs and to respect rate limiting policies.
    """

    def __init__(self, min_interval: float = 0.5):
        """Initialize rate limiter.

        Args:
            min_interval: Minimum seconds between requests (default 0.5s)
        """
        self.min_interval = min_interval
        self.last_request_time = 0.0
        self._lock = Lock()

    def wait_if_needed(self) -> None:
        """Block until minimum interval has elapsed since last request."""
        with self._lock:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self.last_request_time = time.time()

    def reset(self) -> None:
        """Reset the rate limiter."""
        with self._lock:
            self.last_request_time = 0.0


class TokenBucket:
    """Token bucket rate limiter.

    Allows burst traffic up to capacity, but enforces average rate limit
    of tokens_per_second over time.
    """

    def __init__(self, capacity: int, tokens_per_second: float):
        """Initialize token bucket.

        Args:
            capacity: Maximum tokens in bucket
            tokens_per_second: Rate of token generation
        """
        self.capacity = capacity
        self.tokens_per_second = tokens_per_second
        self.tokens = float(capacity)
        self.last_update = time.time()
        self._lock = Lock()

    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """Try to acquire tokens from bucket.

        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait for tokens (None = don't wait)

        Returns:
            True if tokens acquired, False otherwise
        """
        with self._lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            if timeout is None:
                return False

            # Calculate time to wait
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / self.tokens_per_second

            if wait_time > timeout:
                return False

            time.sleep(wait_time)
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def _refill(self) -> None:
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_update

        # Add tokens based on elapsed time
        new_tokens = elapsed * self.tokens_per_second
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now


class AdaptiveRateLimiter:
    """Rate limiter that adapts to rate limit responses from API.

    Detects rate limit errors (429, 503) and automatically increases
    the minimum interval between requests.
    """

    def __init__(self, initial_min_interval: float = 0.5):
        """Initialize adaptive rate limiter.

        Args:
            initial_min_interval: Initial minimum interval between requests
        """
        self.current_interval = initial_min_interval
        self.last_request_time = 0.0
        self._lock = Lock()

    def wait_if_needed(self) -> None:
        """Block until minimum interval has elapsed."""
        with self._lock:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.current_interval:
                time.sleep(self.current_interval - elapsed)
            self.last_request_time = time.time()

    def report_rate_limit_error(self, retry_after: Optional[float] = None) -> None:
        """Report that API rate limit was hit.

        Increases the minimum interval for future requests.

        Args:
            retry_after: Suggested wait time from API (seconds)
        """
        with self._lock:
            if retry_after is not None:
                # Use API's suggested wait time plus buffer
                self.current_interval = retry_after + 1.0
            else:
                # Double the interval (exponential backoff)
                self.current_interval = min(self.current_interval * 2, 30.0)

    def report_success(self) -> None:
        """Report successful request.

        Gradually decreases the minimum interval back to normal.
        """
        with self._lock:
            # Slow recovery: decrease by 10% per success
            self.current_interval *= 0.9

    def reset(self) -> None:
        """Reset rate limiter to initial state."""
        with self._lock:
            self.current_interval = 0.5
            self.last_request_time = 0.0
