"""
Shared test fixtures and configuration for Google Search Agent tests.

This module provides reusable fixtures for testing the Google Search Agent,
including mock search responses, agent instances, and test data.
"""

import pytest
from unittest.mock import Mock, patch
from google_search_agent.agent import create_google_search_agent


@pytest.fixture
def google_search_agent():
    """Create a Google Search Agent instance for testing."""
    return create_google_search_agent()


@pytest.fixture
def mock_google_search_tool():
    """Mock Google Search tool for testing without actual API calls."""
    mock_tool = Mock()
    mock_tool.name = "google_search"
    mock_tool.__str__ = lambda: "google_search"
    return mock_tool


@pytest.fixture
def sample_search_query():
    """Sample search query for testing."""
    return "What is the weather like today?"


@pytest.fixture
def mock_search_success_response():
    """Mock successful Google Search API response."""
    return {
        "status": "success",
        "results": [
            {
                "title": "Weather Today - Local Forecast",
                "url": "https://weather.example.com/today",
                "snippet": (
                    "Today's weather forecast shows sunny skies with a "
                    "high of 75°F and low of 60°F."
                ),
            },
            {
                "title": "Current Weather Conditions",
                "url": "https://example.com/weather/current",
                "snippet": (
                    "Real-time weather data shows clear conditions " "with light winds."
                ),
            },
        ],
        "search_metadata": {
            "query": "weather today",
            "total_results": 2,
            "search_time": 0.5,
        },
    }


@pytest.fixture
def mock_search_error_response():
    """Mock error response from Google Search API."""
    return {
        "status": "error",
        "error_message": "API quota exceeded. Please try again later.",
        "error_code": "QUOTA_EXCEEDED",
    }


@pytest.fixture
def mock_search_empty_response():
    """Mock empty response from Google Search API."""
    return {
        "status": "success",
        "results": [],
        "search_metadata": {
            "query": "very specific search with no results",
            "total_results": 0,
            "search_time": 0.1,
        },
    }


@pytest.fixture
def mock_search_partial_response():
    """Mock partial response with some missing fields."""
    return {
        "status": "success",
        "results": [
            {
                "title": "Partial Result",
                "url": "https://example.com/partial",
                # Missing snippet field
            }
        ],
    }


@pytest.fixture(autouse=True)
def setup_logging():
    """Set up logging for tests to avoid initialization issues."""
    with patch("google_search_agent.agent.setup_logging"):
        with patch("google_search_agent.agent.logger") as mock_logger:
            mock_logger.info = Mock()
            mock_logger.debug = Mock()
            mock_logger.error = Mock()
            mock_logger.warning = Mock()
            yield mock_logger


@pytest.fixture
def mock_agent_with_callbacks():
    """Create an agent with mock callbacks for testing."""
    agent = create_google_search_agent()

    # Add mock callbacks if they exist
    if hasattr(agent, "before_model_callback"):
        agent.before_model_callback = Mock()
    if hasattr(agent, "after_model_callback"):
        agent.after_model_callback = Mock()
    if hasattr(agent, "before_tool_callback"):
        agent.before_tool_callback = Mock()
    if hasattr(agent, "after_tool_callback"):
        agent.after_tool_callback = Mock()

    return agent
