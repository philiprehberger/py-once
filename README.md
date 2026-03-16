# philiprehberger-once

[![Tests](https://github.com/philiprehberger/py-once/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-once/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-once.svg)](https://pypi.org/project/philiprehberger-once/)
[![License](https://img.shields.io/github/license/philiprehberger/py-once)](LICENSE)

Ensure a function runs only once, regardless of how many times it's called.

## Install

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
| `.called` | `bool` for `once`, `dict[key, bool]` for `once_per_key`. Whether the function has been called. |
| `.reset()` | Clear cached result so the function can run again. `once_per_key` accepts an optional `key` argument. |

## License

MIT
