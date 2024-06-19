# Changelog

## 0.1.7 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility
- Add GitHub issue templates, dependabot config, and PR template
## 0.1.6- Add pytest and mypy tool configuration to pyproject.toml

## 0.1.5

- Add basic import test

## 0.1.4

- Add Development section to README

## 0.1.1

- Re-release for PyPI publishing

## 0.1.0 (2026-03-15)

- Initial release
- `once` decorator to ensure a function runs only once with cached result
- `once_per_key` decorator to run once per unique first argument
- Thread-safe with `threading.Lock`
- Async function support for `once`
- `.reset()` and `.called` on all wrappers
