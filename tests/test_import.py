"""Smoke test that the package imports."""


def test_import_smoke() -> None:
    """Verify the package and its public API are importable."""
    from philiprehberger_once import once, once_per_key, once_per_key_async

    assert callable(once)
    assert callable(once_per_key)
    assert callable(once_per_key_async)
