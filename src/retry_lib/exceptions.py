"""Custom exceptions for retry-lib."""

from __future__ import annotations


class RetryError(Exception):
    """Base exception for retry-lib."""


class MaxRetriesExceeded(RetryError):
    """Raised when all retry attempts have been exhausted.

    Attributes
    ----------
    attempts : int
        Number of attempts made.
    last_exception : Exception | None
        The exception from the final attempt.
    """

    def __init__(self, attempts: int, last_exception: Exception | None = None) -> None:
        self.attempts = attempts
        self.last_exception = last_exception
        msg = f"Max retries exceeded after {attempts} attempts"
        if last_exception:
            msg += f": {last_exception}"
        super().__init__(msg)
