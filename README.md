# philiprehberger-once

[![Tests](https://github.com/philiprehberger/py-once/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-once/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-once.svg)](https://pypi.org/project/philiprehberger-once/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-once)](https://github.com/philiprehberger/py-once/commits/main)

Ensure a function runs only once, regardless of how many times it's called.

## Installation

```bash
pip install philiprehberger-once
```

## Usage

```python
from philiprehberger_once import once

@once
def load_config():
    print("Loading...")
    return {"debug": True}

load_config()  # prints "Loading...", returns {"debug": True}
load_config()  # returns {"debug": True} without printing
```

### Async support

```python
import asyncio
from philiprehberger_once import once

@once
async def fetch_token():
    print("Fetching...")
    return "abc-123"

asyncio.run(fetch_token())  # prints "Fetching...", returns "abc-123"
asyncio.run(fetch_token())  # returns "abc-123" without fetching
```

### Once per key

```python
from philiprehberger_once import once_per_key

@once_per_key
def connect(host, port=5432):
    print(f"Connecting to {host}...")
    return f"conn:{host}"

connect("db-1")  # prints "Connecting to db-1...", returns "conn:db-1"
connect("db-1")  # returns cached "conn:db-1"
connect("db-2")  # prints "Connecting to db-2...", returns "conn:db-2"
```

### Once per key (async)

```python
import asyncio
from philiprehberger_once import once_per_key_async

@once_per_key_async
async def fetch_user(user_id: str):
    print(f"Fetching {user_id}...")
    return {"id": user_id}

async def main():
    # Concurrent awaiters of the same key share one in-flight execution.
    a, b, c = await asyncio.gather(
        fetch_user("u1"),
        fetch_user("u1"),
        fetch_user("u2"),
    )
    # Only two prints: one for "u1" and one for "u2".

asyncio.run(main())

# Derive the cache key from a callable instead of the first arg:
@once_per_key_async(key=lambda req, **kw: kw["uid"])
async def load(req, *, uid: str):
    return uid
```

### Once per args

Use the entire call signature (positional + keyword) as the cache key — handy when the value depends on more than just the first argument.

```python
from philiprehberger_once import once_per_args

@once_per_args
def init(host: str, port: int):
    print(f"connecting to {host}:{port}")
    return f"{host}:{port}"

init("a", 1)   # prints, returns "a:1"
init("a", 1)   # cached
init("a", 2)   # prints, returns "a:2"
```

### Cache only on success

Use `@until_success` when you want to retry on failure but cache the first successful result. Exceptions propagate uncached.

```python
from philiprehberger_once import until_success

attempts = 0

@until_success
def load_token():
    global attempts
    attempts += 1
    if attempts < 3:
        raise RuntimeError("temporary failure")
    return "abc-123"

# First two calls raise; third succeeds and is cached forever.
# load_token()  # raises
# load_token()  # raises
load_token()    # returns "abc-123"
load_token()    # returns "abc-123" (cached, not re-invoked)
load_token.succeeded   # True
```

### Forgetting a cached function

`forget(fn)` resets any wrapper in this package from a single entry point — handy when you don't know (or don't care) which decorator was used.

```python
from philiprehberger_once import forget, once, once_per_key

@once
def init():
    return 42

@once_per_key
def connect(host):
    return f"conn:{host}"

init()
connect("db-1")

forget(init)      # True — clears @once cache
forget(connect)   # True — clears all @once_per_key entries
forget(lambda: 1) # False — plain function has no reset()
```

### Reset and inspect

```python
from philiprehberger_once import once

@once
def init():
    return 42

init()
init.called   # True
init.reset()
init.called   # False
init()        # runs again
```

## API

| Function / Property | Description |
|---------------------|-------------|
| `once(fn)` | Decorator. Runs `fn` once, caches and returns the result on subsequent calls. Thread-safe. Supports async. |
| `once_per_key(fn)` | Decorator. Runs `fn` once per unique first argument. Thread-safe. |
| `once_per_args(fn)` | Decorator. Runs `fn` once per unique combination of positional and keyword arguments. Thread-safe. All arguments must be hashable. |
| `once_per_key_async(fn=None, *, key=None)` | Decorator for async functions. Runs the coroutine once per unique key (first positional arg, or derived via `key=...`). Concurrent awaiters of the same key share one in-flight execution. |
| `until_success(fn)` | Decorator. Caches the result only after `fn` returns without raising. Exceptions propagate uncached, so the next call retries. Sync only. Exposes `.succeeded` and `.reset()`. |
| `forget(fn)` | Reset any wrapper in this package (`@once`, `@once_per_key`, `@once_per_args`, `@once_per_key_async`, `@until_success`). Returns `True` on success, `False` if `fn` has no `reset()` method. |
| `.called` | `bool` for `once`, `dict[key, bool]` for `once_per_key` and `once_per_key_async`. Whether the function has been called. |
| `.reset()` | Clear cached result so the function can run again. `once_per_key` and `once_per_key_async` accept an optional `key` argument. |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-once)

🐛 [Report issues](https://github.com/philiprehberger/py-once/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-once/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
