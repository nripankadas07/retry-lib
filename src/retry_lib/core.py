"""Core retry decorator."""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable, Generator, TypeVar

from retry_lib.backoff import exponential
from retry_lib.exceptions import MaxRetriesExceeded

logger = logging.getLogger("retry_lib")

F = TypeVar("F", bound=Callable[..., Any])


def retry(
    max_attempts: int = 3,
    backoff: Generator[float, None, None] | None = None,
    retry_on: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception, float], None] | None = None,
) -> Callable[[F], F]:
    """Decorator that retries a function on failure.

    Parameters
    ----------
    max_attempts:
        Total number of attempts (including the first call). Must be >= 1.
    backoff:
        A generator yielding delay (seconds) between attempts. Defaults to
        exponential backoff starting at 1 s.
    retry_on:
        Tuple of exception types that trigger a retry. Other exceptions
        propagate immediately.
    on_retry:
        Optional callback ``(attempt: int, error: Exception, delay: float) -> None``
        invoked before each retry sleep.

    Raises
    ------
    MaxRetriesExceeded
        When all attempts are exhausted.
    ValueError
        If *max_attempts* < 1.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delays = backoff if backoff is not None else exponential()
            last_exc: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        raise MaxRetriesExceeded(attempt, exc) from exc
                    delay = next(delays)
                    logger.debug(
                        "Attempt %d/%d for %s failed: %s. Retrying in %.2fs",
                        attempt,
                        max_attempts,
                        func.__name__,
                        exc,
                        delay,
                    )
                    if on_retry is not None:
                        on_retry(attempt, exc, delay)
                    time.sleep(delay)

            # Should be unreachable, but satisfy type checkers
            raise MaxRetriesExceeded(max_attempts, last_exc)  # pragma: no cover

        return wrapper  # type: ignore[return-value]

    return decorator
