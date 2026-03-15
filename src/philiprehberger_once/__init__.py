"""Ensure a function runs only once, regardless of how many times it's called."""

from __future__ import annotations

import asyncio
import functools
import threading
from typing import Any, Callable, TypeVar

__all__ = ["once", "once_per_key"]

F = TypeVar("F", bound=Callable[..., Any])


class _OnceWrapper:
    """Wrapper that ensures a function runs only once and caches the result."""

    def __init__(self, fn: Callable[..., Any]) -> None:
        self._fn = fn
        self._lock = threading.Lock()
        self._called = False
        self._result: Any = None
        functools.update_wrapper(self, fn)

    @property
    def called(self) -> bool:
        """Whether the wrapped function has been called."""
        return self._called

    def reset(self) -> None:
        """Reset state so the function can be called again."""
        with self._lock:
            self._called = False
            self._result = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._called:
            return self._result
        with self._lock:
            if not self._called:
                self._result = self._fn(*args, **kwargs)
                self._called = True
        return self._result


class _AsyncOnceWrapper:
    """Wrapper that ensures an async function runs only once and caches the result."""

    def __init__(self, fn: Callable[..., Any]) -> None:
        self._fn = fn
        self._lock = asyncio.Lock()
        self._called = False
        self._result: Any = None
        functools.update_wrapper(self, fn)

    @property
    def called(self) -> bool:
        """Whether the wrapped function has been called."""
        return self._called

    def reset(self) -> None:
        """Reset state so the function can be called again."""
        self._called = False
        self._result = None

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._called:
            return self._result
        async with self._lock:
            if not self._called:
                self._result = await self._fn(*args, **kwargs)
                self._called = True
        return self._result


def once(fn: F) -> F:
    """Decorator that ensures a function runs only once and caches the result.

    Thread-safe for synchronous functions. Supports async functions.
    The wrapper exposes a ``.reset()`` method to clear the cached result
    and a ``.called`` property to check whether the function has executed.

    Args:
        fn: The function to wrap.

    Returns:
        A wrapped version of *fn* that executes at most once.
    """
    if asyncio.iscoroutinefunction(fn):
        return _AsyncOnceWrapper(fn)  # type: ignore[return-value]
    return _OnceWrapper(fn)  # type: ignore[return-value]


class _OncePerKeyWrapper:
    """Wrapper that ensures a function runs only once per unique first argument."""

    def __init__(self, fn: Callable[..., Any]) -> None:
        self._fn = fn
        self._lock = threading.Lock()
        self._results: dict[Any, Any] = {}
        functools.update_wrapper(self, fn)

    @property
    def called(self) -> dict[Any, bool]:
        """Mapping of keys to whether the function has been called for that key."""
        with self._lock:
            return {key: True for key in self._results}

    def reset(self, key: Any = None) -> None:
        """Reset cached results.

        Args:
            key: If provided, reset only the given key. Otherwise reset all keys.
        """
        with self._lock:
            if key is None:
                self._results.clear()
            else:
                self._results.pop(key, None)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not args:
            raise TypeError(
                f"{self._fn.__name__}() requires at least one positional argument as key"
            )
        key = args[0]
        if key in self._results:
            return self._results[key]
        with self._lock:
            if key not in self._results:
                self._results[key] = self._fn(*args, **kwargs)
        return self._results[key]


def once_per_key(fn: F) -> F:
    """Decorator that ensures a function runs only once per unique first argument.

    Thread-safe. The first positional argument is used as the cache key.
    The wrapper exposes a ``.reset(key=None)`` method to clear cached results
    (all keys if *key* is ``None``, or a specific key) and a ``.called``
    property returning a dict of keys that have been invoked.

    Args:
        fn: The function to wrap.

    Returns:
        A wrapped version of *fn* that executes at most once per unique first argument.
    """
    return _OncePerKeyWrapper(fn)  # type: ignore[return-value]
