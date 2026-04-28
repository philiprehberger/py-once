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
| `once_per_key_async(fn=None, *, key=None)` | Decorator for async functions. Runs the coroutine once per unique key (first positional arg, or derived via `key=...`). Concurrent awaiters of the same key share one in-flight execution. |
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
