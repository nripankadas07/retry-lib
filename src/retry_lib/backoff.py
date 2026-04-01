"""Backoff strategy generators for retry delays."""

from __future__ import annotations

from typing import Generator
import random


def constant(delay: float = 1.0) -> Generator[float, None, None]:
    """Yield a constant delay on every retry."""
    while True:
        yield delay


def linear(initial: float = 1.0, increment: float = 1.0, maximum: float = 60.0) -> Generator[float, None, None]:
    """Yield linearly increasing delays: initial, initial+increment, initial+2*increment, ..."""
    current = initial
    while True:
        yield min(current, maximum)
        current += increment


def exponential(
    initial: float = 1.0,
    multiplier: float = 2.0,
    maximum: float = 60.0,
    jitter: bool = False,
) -> Generator[float, None, None]:
    """Yield exponentially increasing delays with optional jitter."""
    current = initial
    while True:
        delay = min(current, maximum)
        if jitter:
            delay = random.uniform(0, delay)  # noqa: S311
        yield delay
        current *= multiplier


def fibonacci(initial: float = 1.0, maximum: float = 60.0) -> Generator[float, None, None]:
    """Yield Fibonacci-sequence delays scaled by *initial*."""
    a, b = 0.0, initial
    while True:
        yield min(b, maximum)
        a, b = b, a + b
