# Conditionally load requests_mock plugin only if available
# This import is used for pytest plugin configuration
try:
    import requests_mock  # noqa: F401 # Used by pytest plugin system

    # Configure pytest plugins for requests_mock if available
    # pytest_plugins is used by pytest's plugin loading system
    pytest_plugins = ["requests_mock"]  # noqa: F841 # Used by pytest
except ImportError:
    # Fall back to empty plugin list if requests_mock not available
    # pytest_plugins is used by pytest's plugin loading system
    pytest_plugins = []  # noqa: F841 # Used by pytest
