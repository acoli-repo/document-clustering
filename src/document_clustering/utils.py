"""Miscellaneous functions that would be lonely in their seperate files.

Bad style, I know, but I made up for it in documentation!
"""

import datetime
import logging
import shelve
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from time import perf_counter
from typing import TypeVar

logger = logging.getLogger(__name__)

# Memoize

T = TypeVar("T")

def get_cache_dir() -> Path:
    """Create cache directory and return Path."""
    cache_dir = Path.home() / ".cache" / "document-clustering"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def shelve_memoize(filename: str) -> Callable[[str], T]:
    """On-disk cache decorator using shelve."""

    def decorator_shelve_memoize(func: Callable[[str], T]):
        @wraps(func)
        def wrapper_shelve_memoize(arxiv_id: str):
            with shelve.open(str(get_cache_dir() / filename)) as db:  # noqa: S301
                if arxiv_id not in db:
                    logger.debug(f"Cache miss for {filename}! Fetching {arxiv_id} ...")
                    db[arxiv_id] = func(arxiv_id)
                return db.get(arxiv_id)

        return wrapper_shelve_memoize

    return decorator_shelve_memoize


def shelve_forget(filename: str, arxiv_id: str) -> None:
    """Clear a specific item from the shelve.

    Parameters
    ----------
    filename (str): The cache-file to use
    arxiv_id (str): The document to remove from cache
    """
    with shelve.open(str(get_cache_dir() / filename)) as db:  # noqa: S301
        del db[arxiv_id]


# Track execution time


@contextmanager
def execution_time() -> Generator[Callable[[], datetime.timedelta], None, None]:
    """Log the runtime of the decorated function."""
    t0 = t1 = perf_counter()

    def get_time_delta():
        return datetime.timedelta(seconds=t1 - t0)

    yield get_time_delta
    t1 = perf_counter()
    return
