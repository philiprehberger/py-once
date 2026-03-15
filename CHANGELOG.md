# Changelog

## 0.1.0 (2026-03-15)

- Initial release
- `once` decorator to ensure a function runs only once with cached result
- `once_per_key` decorator to run once per unique first argument
- Thread-safe with `threading.Lock`
- Async function support for `once`
- `.reset()` and `.called` on all wrappers
