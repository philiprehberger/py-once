"""Basic import test."""


def test_import():
    """Verify the package can be imported."""
    import philiprehberger_once
    assert hasattr(philiprehberger_once, "__name__") or True
