# Changelog

## 0.3.0 (2026-04-28)

- Add `once_per_args` decorator — keys on the full call signature (all positional + keyword args), unlike `once_per_key` which only keys on the first positional arg
- Sync `pyproject.toml` description to end with a period (matches README one-liner)

## 0.2.0 (2026-04-27)

- Add `once_per_key_async` decorator for memoizing async coroutines per-key with shared in-flight execution
- Replace import-only test with comprehensive test suite

## 0.1.7 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility
- Add GitHub issue templates, dependabot config, and PR template

## 0.1.6 (2026-03-29)

- Add pytest and mypy tool configuration to pyproject.toml

## 0.1.5 (2026-03-25)

- Add basic import test

## 0.1.4 (2026-03-22)

- Add Development section to README

## 0.1.1 (2026-03-16)

- Re-release for PyPI publishing

## 0.1.0 (2026-03-15)

- Initial release
- `once` decorator to ensure a function runs only once with cached result
- `once_per_key` decorator to run once per unique first argument
- Thread-safe with `threading.Lock`
- Async function support for `once`
- `.reset()` and `.called` on all wrappers
