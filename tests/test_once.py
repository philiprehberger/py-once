"""Tests for philiprehberger_once."""

from __future__ import annotations

import asyncio

import pytest

from philiprehberger_once import once, once_per_args, once_per_key, once_per_key_async


# ---------------------------------------------------------------------------
# once (sync)
# ---------------------------------------------------------------------------


def test_once_runs_only_once_and_caches_result() -> None:
    counter = {"n": 0}

    @once
    def init() -> int:
        counter["n"] += 1
        return 42

    assert init() == 42
    assert init() == 42
    assert init() == 42
    assert counter["n"] == 1


def test_once_called_toggles_and_reset_clears() -> None:
    @once
    def init() -> str:
        return "ok"

    assert init.called is False
    init()
    assert init.called is True
    init.reset()
    assert init.called is False
    assert init() == "ok"
    assert init.called is True


# ---------------------------------------------------------------------------
# once (async)
# ---------------------------------------------------------------------------


def test_once_async_runs_only_once_and_caches_result() -> None:
    counter = {"n": 0}

    @once
    async def fetch() -> str:
        counter["n"] += 1
        return "abc"

    async def run() -> tuple[str, str, str]:
        a = await fetch()
        b = await fetch()
        c = await fetch()
        return a, b, c

    a, b, c = asyncio.run(run())
    assert a == b == c == "abc"
    assert counter["n"] == 1


def test_once_async_reset_allows_rerun() -> None:
    counter = {"n": 0}

    @once
    async def fetch() -> int:
        counter["n"] += 1
        return counter["n"]

    async def run() -> tuple[int, int]:
        first = await fetch()
        fetch.reset()
        second = await fetch()
        return first, second

    first, second = asyncio.run(run())
    assert first == 1
    assert second == 2
    assert counter["n"] == 2


# ---------------------------------------------------------------------------
# once_per_key (sync)
# ---------------------------------------------------------------------------


def test_once_per_key_distinct_keys_execute_independently() -> None:
    counter = {"n": 0}

    @once_per_key
    def connect(host: str) -> str:
        counter["n"] += 1
        return f"conn:{host}"

    assert connect("a") == "conn:a"
    assert connect("b") == "conn:b"
    assert counter["n"] == 2


def test_once_per_key_repeated_key_runs_once() -> None:
    counter = {"n": 0}

    @once_per_key
    def connect(host: str) -> str:
        counter["n"] += 1
        return f"conn:{host}"

    assert connect("a") == "conn:a"
    assert connect("a") == "conn:a"
    assert connect("a") == "conn:a"
    assert counter["n"] == 1
    assert connect.called == {"a": True}


def test_once_per_key_reset_specific_and_all() -> None:
    counter = {"n": 0}

    @once_per_key
    def connect(host: str) -> str:
        counter["n"] += 1
        return f"conn:{host}-{counter['n']}"

    connect("a")
    connect("b")
    assert counter["n"] == 2

    connect.reset("a")
    assert connect.called == {"b": True}
    connect("a")
    assert counter["n"] == 3

    connect.reset()
    assert connect.called == {}
    connect("a")
    connect("b")
    assert counter["n"] == 5


def test_once_per_key_requires_positional_argument() -> None:
    @once_per_key
    def f(*args: object, **kwargs: object) -> None:
        return None

    with pytest.raises(TypeError):
        f()


# ---------------------------------------------------------------------------
# once_per_key_async (new)
# ---------------------------------------------------------------------------


def test_once_per_key_async_bare_uses_first_arg_as_key() -> None:
    counter = {"n": 0}

    @once_per_key_async
    async def fetch(host: str) -> str:
        counter["n"] += 1
        return f"data:{host}"

    async def run() -> tuple[str, str, str]:
        a = await fetch("a")
        a2 = await fetch("a")
        b = await fetch("b")
        return a, a2, b

    a, a2, b = asyncio.run(run())
    assert a == a2 == "data:a"
    assert b == "data:b"
    assert counter["n"] == 2


def test_once_per_key_async_with_explicit_key_callable() -> None:
    counter = {"n": 0}

    @once_per_key_async(key=lambda x, **kw: kw["uid"])
    async def load(x: int, *, uid: str) -> str:
        counter["n"] += 1
        return f"{uid}:{x}"

    async def run() -> list[str]:
        results = []
        results.append(await load(1, uid="u1"))
        results.append(await load(2, uid="u1"))  # cached on uid=u1
        results.append(await load(3, uid="u2"))
        return results

    results = asyncio.run(run())
    assert results[0] == "u1:1"
    assert results[1] == "u1:1"  # cached, reused
    assert results[2] == "u2:3"
    assert counter["n"] == 2


def test_once_per_key_async_concurrent_awaiters_share_in_flight_execution() -> None:
    counter = {"n": 0}
    started = asyncio.Event()
    release = asyncio.Event()

    @once_per_key_async
    async def fetch(host: str) -> str:
        counter["n"] += 1
        started.set()
        await release.wait()
        return f"data:{host}"

    async def run() -> list[str]:
        # Schedule 10 concurrent awaiters with the same key.
        tasks = [asyncio.create_task(fetch("same")) for _ in range(10)]
        # Wait for the first one to start, then release.
        await started.wait()
        release.set()
        return await asyncio.gather(*tasks)

    results = asyncio.run(run())
    assert all(r == "data:same" for r in results)
    assert counter["n"] == 1


def test_once_per_key_async_distinct_keys_execute_independently() -> None:
    counter = {"n": 0}

    @once_per_key_async
    async def fetch(host: str) -> str:
        counter["n"] += 1
        return f"data:{host}"

    async def run() -> tuple[str, str, str]:
        a, b, c = await asyncio.gather(fetch("a"), fetch("b"), fetch("c"))
        return a, b, c

    a, b, c = asyncio.run(run())
    assert a == "data:a"
    assert b == "data:b"
    assert c == "data:c"
    assert counter["n"] == 3


def test_once_per_key_async_reset_specific_and_all() -> None:
    counter = {"n": 0}

    @once_per_key_async
    async def fetch(host: str) -> int:
        counter["n"] += 1
        return counter["n"]

    async def run() -> dict[str, object]:
        await fetch("a")
        await fetch("b")
        called_after_two = dict(fetch.called)

        fetch.reset("a")
        called_after_reset_a = dict(fetch.called)
        await fetch("a")
        n_after_rerun_a = counter["n"]

        fetch.reset()
        called_after_reset_all = dict(fetch.called)
        await fetch("a")
        await fetch("b")
        return {
            "called_after_two": called_after_two,
            "called_after_reset_a": called_after_reset_a,
            "n_after_rerun_a": n_after_rerun_a,
            "called_after_reset_all": called_after_reset_all,
            "n_final": counter["n"],
        }

    state = asyncio.run(run())
    assert state["called_after_two"] == {"a": True, "b": True}
    assert state["called_after_reset_a"] == {"b": True}
    assert state["n_after_rerun_a"] == 3
    assert state["called_after_reset_all"] == {}
    assert state["n_final"] == 5


def test_once_per_key_async_rejects_sync_function_bare() -> None:
    with pytest.raises(TypeError):

        @once_per_key_async
        def not_async(host: str) -> str:
            return host


def test_once_per_args_distinct_args_execute_independently() -> None:
    counter = {"n": 0}

    @once_per_args
    def init(host: str, port: int) -> str:
        counter["n"] += 1
        return f"{host}:{port}"

    assert init("a", 1) == "a:1"
    assert init("a", 2) == "a:2"
    assert init("b", 1) == "b:1"
    assert counter["n"] == 3


def test_once_per_args_repeated_args_run_once() -> None:
    counter = {"n": 0}

    @once_per_args
    def init(host: str, port: int) -> str:
        counter["n"] += 1
        return f"{host}:{port}"

    init("a", 1)
    init("a", 1)
    init("a", 1)
    assert counter["n"] == 1


def test_once_per_args_kwargs_keyed() -> None:
    counter = {"n": 0}

    @once_per_args
    def init(*, host: str, port: int) -> str:
        counter["n"] += 1
        return f"{host}:{port}"

    init(host="a", port=1)
    init(host="a", port=1)
    init(host="a", port=2)
    assert counter["n"] == 2


def test_once_per_args_reset_specific_and_all() -> None:
    counter = {"n": 0}

    @once_per_args
    def init(x: int) -> int:
        counter["n"] += 1
        return counter["n"]

    init(1)
    init(2)
    assert counter["n"] == 2

    init.reset(1)
    init(1)
    assert counter["n"] == 3

    init.reset()
    init(1)
    init(2)
    assert counter["n"] == 5


def test_once_per_key_async_rejects_sync_function_with_key() -> None:
    with pytest.raises(TypeError):

        @once_per_key_async(key=lambda x: x)
        def not_async(x: int) -> int:
            return x
