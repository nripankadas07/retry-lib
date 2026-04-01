# retry-lib

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

A zero-dependency Python retry decorator with pluggable backoff strategies — constant, linear, exponential (with jitter), and Fibonacci.

## Why

Transient failures happen: network timeouts, rate limits, flaky services. `retry-lib` gives you a clean decorator interface with full control over retry count, backoff timing, exception filtering, and lifecycle callbacks.

## Installation

```bash
pip install .
```

Or for development:

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Retry

```python
from retry_lib import retry

@retry(max_attempts=3)
def fetch_data():
    # raises on transient failure
    return requests.get("https://api.example.com/data").json()
```

### Custom Backoff

```python
from retry_lib import retry, exponential, linear, fibonacci, constant

# Exponential backoff with jitter, max 30s
@retry(max_attempts=5, backoff=exponential(initial=1.0, multiplier=2.0, maximum=30.0, jitter=True))
def call_api():
    ...

# Linear backoff: 1s, 3s, 5s, 7s, ...
@retry(max_attempts=4, backoff=linear(initial=1.0, increment=2.0))
def poll_status():
    ...

# Fibonacci backoff: 1, 1, 2, 3, 5, 8, ...
@retry(max_attempts=6, backoff=fibonacci())
def connect():
    ...
```

### Selective Exception Handling

```python
from retry_lib import retry

@retry(max_attempts=3, retry_on=(ConnectionError, TimeoutError))
def upload(data):
    # Only retries on ConnectionError or TimeoutError
    # ValueError, TypeError, etc. propagate immediately
    ...
```

### Retry Callback

```python
from retry_lib import retry, constant

def log_retry(attempt: int, error: Exception, delay: float):
    print(f"Attempt {attempt} failed: {error}. Retrying in {delay}s...")

@retry(max_attempts=5, backoff=constant(2.0), on_retry=log_retry)
def flaky_operation():
    ...
```

### Exception Handling

```python
from retry_lib import retry, MaxRetriesExceeded, constant

@retry(max_attempts=3, backoff=constant(0))
def always_fails():
    raise RuntimeError("boom")

try:
    always_fails()
except MaxRetriesExceeded as e:
    print(f"Failed after {e.attempts} attempts: {e.last_exception}")
```

## API Reference

| Symbol | Description |
|--------|-------------|
| `retry(max_attempts, backoff, retry_on, on_retry)` | Decorator that retries a function on failure |
| `constant(delay)` | Constant delay generator |
| `linear(initial, increment, maximum)` | Linearly increasing delay |
| `exponential(initial, multiplier, maximum, jitter)` | Exponential backoff with optional jitter |
| `fibonacci(initial, maximum)` | Fibonacci-sequence delays |
| `MaxRetriesExceeded` | Raised when all attempts fail |
| `RetryError` | Base exception class |

## Architecture

```
src/retry_lib/
├── __init__.py       # Public API
├── core.py           # retry() decorator
├── backoff.py        # Backoff strategy generators
└── exceptions.py     # Custom exceptions
```

The retry decorator wraps any callable and catches specified exception types. On failure it pulls the next delay from a backoff generator, invokes an optional callback, sleeps, and retries. Backoff strategies are plain Python generators, making it trivial to create custom strategies.

## License

MIT — Nripanka Das
