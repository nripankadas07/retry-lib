"""Tests for retry-lib."""

from __future__ import annotations

import pytest

from retry_lib.core import retry
from retry_lib.backoff import constant, exponential, linear, fibonacci
from retry_lib.exceptions import MaxRetriesExceeded, RetryError


# ---------- backoff strategy tests ----------


def test_constant_backoff():
    gen = constant(2.5)
    assert [next(gen) for _ in range(4)] == [2.5, 2.5, 2.5, 2.5]


def test_linear_backoff():
    gen = linear(initial=1.0, increment=2.0, maximum=10.0)
    vals = [next(gen) for _ in range(6)]
    assert vals == [1.0, 3.0, 5.0, 7.0, 9.0, 10.0]


def test_exponential_backoff():
    gen = exponential(initial=1.0, multiplier=2.0, maximum=16.0, jitter=False)
    vals = [next(gen) for _ in range(6)]
    assert vals == [1.0, 2.0, 4.0, 8.0, 16.0, 16.0]


def test_exponential_jitter_within_bounds():
    gen = exponential(initial=4.0, multiplier=2.0, maximum=100.0, jitter=True)
    for _ in range(20):
        val = next(gen)
        assert 0 <= val <= 100.0


def test_fibonacci_backoff():
    gen = fibonacci(initial=1.0, maximum=20.0)
    vals = [next(gen) for _ in range(8)]
    assert vals == [1.0, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 20.0]


# ---------- retry decorator tests ----------


def test_retry_succeeds_immediately():
    call_count = 0

    @retry(max_attempts=3, backoff=constant(0))
    def succeed():
        nonlocal call_count
        call_count += 1
        return "ok"

    assert succeed() == "ok"
    assert call_count == 1


def test_retry_succeeds_on_second_attempt():
    call_count = 0

    @retry(max_attempts=3, backoff=constant(0))
    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("not yet")
        return "ok"

    assert flaky() == "ok"
    assert call_count == 2


def test_retry_exhausts_attempts():
    @retry(max_attempts=3, backoff=constant(0))
    def always_fail():
        raise RuntimeError("boom")

    with pytest.raises(MaxRetriesExceeded) as exc_info:
        always_fail()
    assert exc_info.value.attempts == 3
    assert isinstance(exc_info.value.last_exception, RuntimeError)


def test_retry_only_catches_specified_exceptions():
    call_count = 0

    @retry(max_attempts=5, backoff=constant(0), retry_on=(ValueError,))
    def raise_type_error():
        nonlocal call_count
        call_count += 1
        raise TypeError("wrong type")

    with pytest.raises(TypeError):
        raise_type_error()
    assert call_count == 1  # No retry because TypeError isn't in retry_on


def test_retry_on_callback():
    attempts_seen: list[int] = []

    def tracker(attempt: int, error: Exception, delay: float) -> None:
        attempts_seen.append(attempt)

    @retry(max_attempts=3, backoff=constant(0), on_retry=tracker)
    def flaky():
        if len(attempts_seen) < 2:
            raise ValueError("fail")
        return "done"

    assert flaky() == "done"
    assert attempts_seen == [1, 2]


def test_retry_invalid_max_attempts():
    with pytest.raises(ValueError, match="max_attempts must be >= 1"):
        retry(max_attempts=0)


# ---------- exception tests ----------


def test_max_retries_exceeded_is_retry_error():
    exc = MaxRetriesExceeded(3)
    assert isinstance(exc, RetryError)
    assert "3 attempts" in str(exc)


def test_max_retries_exceeded_with_cause():
    cause = IOError("disk full")
    exc = MaxRetriesExceeded(5, cause)
    assert exc.last_exception is cause
    assert "disk full" in str(exc)
