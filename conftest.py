# Conditionally load requests_mock plugin only if available
try:
    import requests_mock  # noqa: F401

    pytest_plugins = ["requests_mock"]
except ImportError:
    pytest_plugins = []
