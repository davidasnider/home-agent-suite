"""
Integration Test Configuration and Fixtures

This module provides shared fixtures and configuration for integration tests
between agents, tools, and the Streamlit application.
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch
from httpx import Response
import requests_mock

# Add agents and libs to Python path for testing
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
agents_dir = os.path.join(project_root, "agents")
libs_dir = os.path.join(project_root, "libs")

for dir_path in [agents_dir, libs_dir]:
    if dir_path not in sys.path:
        sys.path.insert(0, dir_path)


@pytest.fixture
def mock_tomorrow_io_response():
    """Provides a standard Tomorrow.io API response for testing"""
    return {
        "timelines": {
            "hourly": [
                {
                    "time": "2025-09-28T14:00:00Z",
                    "values": {
                        "temperature": 75,
                        "humidity": 65,
                        "windSpeed": 8.5,
                        "weatherCode": 1000,  # Clear sky
                        "precipitationProbability": 10,
                    },
                },
                {
                    "time": "2025-09-28T15:00:00Z",
                    "values": {
                        "temperature": 76,
                        "humidity": 62,
                        "windSpeed": 9.2,
                        "weatherCode": 1000,
                        "precipitationProbability": 5,
                    },
                },
            ]
        }
    }


@pytest.fixture
def mock_google_search_response():
    """Provides a standard Google Search API response for testing"""
    return {
        "items": [
            {
                "title": "Paris Tourism - Official Site",
                "snippet": "Discover the top attractions in Paris including the Eiffel Tower, Louvre Museum, and Notre Dame Cathedral.",
                "link": "https://www.paris-tourism.com",
            },
            {
                "title": "10 Best Things to Do in Paris",
                "snippet": "From iconic landmarks to hidden gems, explore the best activities and attractions in the City of Light.",
                "link": "https://www.travel-guide.com/paris",
            },
        ]
    }


@pytest.fixture
def mock_llm_response():
    """Provides a standard LLM response for testing"""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "Based on the weather data, I recommend outdoor activities between 2-4 PM when temperatures will be around 75-76F with clear skies."
                        }
                    ],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }


@pytest.fixture
def mock_supervisor_llm_response():
    """Provides a standard supervisor agent LLM response for testing"""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "I'll help you with the weather information. Let me check the current conditions."
                        }
                    ],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }


@pytest.fixture
def mock_google_adk_client():
    """Mock the Google ADK client to avoid real API calls"""

    def mock_llm_call(*args, **kwargs):
        """Mock LLM calls to return predefined responses"""
        if "generateContent" in kwargs.get("url", ""):
            return Response(
                200,
                json={
                    "candidates": [
                        {
                            "content": {
                                "parts": [{"text": "Mock LLM response"}],
                                "role": "model",
                            },
                            "finish_reason": "STOP",
                        }
                    ]
                },
                headers={"content-type": "application/json"},
            )
        return Response(200, json={}, headers={"content-type": "application/json"})

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        yield mock_llm_call


@pytest.fixture
def day_planner_agent():
    """Creates a day planner agent for testing"""
    # Add required directories to path
    day_planner_dir = os.path.join(agents_dir, "day_planner")
    if day_planner_dir not in sys.path:
        sys.path.insert(0, day_planner_dir)

    from day_planner.agent import create_day_planner_agent

    return create_day_planner_agent()


@pytest.fixture
def google_search_agent():
    """Creates a google search agent for testing"""
    # Add required directories to path
    google_search_dir = os.path.join(agents_dir, "google_search_agent")
    if google_search_dir not in sys.path:
        sys.path.insert(0, google_search_dir)

    from google_search_agent.agent import create_google_search_agent

    return create_google_search_agent()


@pytest.fixture
def supervisor_agent():
    """Creates a supervisor agent for testing"""
    # Add required directories to path
    supervisor_dir = os.path.join(agents_dir, "supervisor", "src")
    if supervisor_dir not in sys.path:
        sys.path.insert(0, supervisor_dir)

    from supervisor.agent import create_supervisor_agent

    return create_supervisor_agent()


@pytest.fixture
def setup_api_mocks(
    requests_mock, mock_tomorrow_io_response, mock_google_search_response
):
    """Sets up all external API mocks for testing"""
    # Mock Tomorrow.io API
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast", json=mock_tomorrow_io_response
    )

    # Mock Google Search API
    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1", json=mock_google_search_response
    )

    return {
        "tomorrow_io": mock_tomorrow_io_response,
        "google_search": mock_google_search_response,
    }


@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state for testing"""
    mock_state = Mock()
    mock_state.messages = []
    mock_state.agent = None
    mock_state.session_id = "test_session_123"
    return mock_state


@pytest.fixture
def sample_conversation_history():
    """Provides sample conversation history for testing"""
    return [
        {"role": "user", "content": "What's the weather like today?"},
        {"role": "assistant", "content": "I'll check the weather for you."},
        {"role": "user", "content": "What about tomorrow?"},
        {"role": "assistant", "content": "Let me get tomorrow's forecast."},
    ]
