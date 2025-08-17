# Conditionally load requests_mock plugin only if available
try:
    import requests_mock  # noqa: F401

    # Configure pytest plugins for requests_mock if available
    pytest_plugins = ["requests_mock"]  # noqa: F841
except ImportError:
    # Fall back to empty plugin list if requests_mock not available
    pytest_plugins = []  # noqa: F841
