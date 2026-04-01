"""retry-lib: Configurable retry decorator library with backoff strategies."""

__version__ = "0.1.0"

from retry_lib.core import retry
from retry_lib.backoff import constant, exponential, linear, fibonacci
from retry_lib.exceptions import MaxRetriesExceeded, RetryError
