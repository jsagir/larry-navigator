"""
Rate Limiter for Gemini API Calls
Inspired by best practices from Gemini RAG implementations
"""

import time
from typing import Callable, Any
from functools import wraps

class RateLimiter:
    """
    Simple rate limiter for API calls
    Gemini API limits: ~60 requests per minute for File Search
    """

    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0

    def wait_if_needed(self):
        """Wait if we're calling too frequently"""
        now = time.time()
        time_since_last = now - self.last_call

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_call = time.time()


def with_retry(max_retries: int = 3, backoff_factor: float = 2.0):
    """
    Decorator for retrying API calls with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Multiplier for wait time between retries
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()

                    # Don't retry for certain errors
                    if any(x in error_msg for x in ['invalid', 'not found', 'forbidden']):
                        raise

                    # Retry for rate limits and temporary errors
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt
                        print(f"⚠️ Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Max retries reached: {e}")

            raise last_exception

        return wrapper
    return decorator


# Global rate limiter instance
gemini_rate_limiter = RateLimiter(calls_per_minute=60)
