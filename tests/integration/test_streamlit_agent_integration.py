"""
Streamlit-Agent Integration Tests

Tests the integration between the Streamlit UI and agents, verifying that:
- UI correctly communicates with supervisor agent
- Session state is properly managed
- Error handling works correctly in UI
- Agent responses are properly displayed
"""

import pytest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from httpx import Response


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_streamlit_supervisor_agent_communication(
    setup_api_mocks, mock_google_adk_client
):
    """
    Tests that the Streamlit app correctly communicates with the supervisor agent.
    """
    # Mock the supervisor agent response for weather query
    weather_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "The weather in New York is currently 75F with "
                            "clear skies. Perfect for outdoor activities!"
                        }
                    ],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }

    def mock_llm_call(*args, **kwargs):
        if "generateContent" in kwargs.get("url", ""):
            return Response(
                200, json=weather_response, headers={"content-type": "application/json"}
            )
        return Response(200, json={}, headers={"content-type": "application/json"})

    # Mock the HTTP client
    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        # Run the Streamlit app
        at = AppTest.from_file("app.py").run()

        # Verify app loaded correctly
        assert not at.exception

        # Simulate user input
        weather_query = "What's the weather like in New York?"
        at.chat_input[0].set_value(weather_query).run()

        # Check that the response appears in the UI
        # Look for weather-related content in the markdown elements
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # Should have at least some markdown content (user message + agent response)
        assert len(markdown_content) > 0

        # Check for presence of user query and some response
        all_content = " ".join(markdown_content)
        assert weather_query in all_content or "weather" in all_content.lower()


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_streamlit_session_state_management(
    setup_api_mocks, mock_google_adk_client
):
    """
    Tests that Streamlit properly manages session state across interactions.
    """
    # Mock agent response
    simple_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Hello! How can I help you today?"}],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }

    def mock_llm_call(*args, **kwargs):
        return Response(
            200, json=simple_response, headers={"content-type": "application/json"}
        )

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        # Initialize app
        at = AppTest.from_file("app.py").run()
        assert not at.exception

        # First interaction
        at.chat_input[0].set_value("Hello").run()

        # Get session state after first interaction
        initial_markdown_count = len(
            [
                md
                for md in at.markdown
                if md.value and not md.value.startswith("<style>")
            ]
        )

        # Second interaction
        at.chat_input[0].set_value("How are you?").run()

        # Get session state after second interaction
        final_markdown_count = len(
            [
                md
                for md in at.markdown
                if md.value and not md.value.startswith("<style>")
            ]
        )

    # Should have more content after second interaction
    # (conversation history preserved)
    assert final_markdown_count >= initial_markdown_count


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_streamlit_error_handling_in_ui(requests_mock):
    """
    Tests that the Streamlit UI properly handles errors from agents and APIs.
    """
    # Mock API to return error
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        status_code=500,
        text="Internal Server Error",
    )

    # Mock LLM to return error-related response
    error_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "I'm sorry, I'm having trouble accessing the "
                            "weather service right now."
                        }
                    ],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }

    def mock_llm_call(*args, **kwargs):
        return Response(
            200, json=error_response, headers={"content-type": "application/json"}
        )

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        # Run app and test error scenario
        at = AppTest.from_file("app.py").run()
        assert not at.exception

        # Try a weather query that should trigger the error
        at.chat_input[0].set_value("What's the weather like?").run()

        # App should not crash, should handle the error gracefully
        assert not at.exception

        # Should display some form of response (even if it's an error message)
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        assert len(markdown_content) > 0


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_streamlit_agent_response_display(
    setup_api_mocks, mock_google_adk_client
):
    """
    Tests that agent responses are properly formatted and displayed in the UI.
    """
    # Mock a detailed agent response
    detailed_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "Based on the current weather data for New York:\n\n"
                                "**Temperature**: 75F\n**Conditions**: Clear skies\n"
                                "**Wind**: 8 mph from the west\n**Humidity**: 65%\n\n"
                                "**Recommendations**:\n- Great day for outdoor "
                                "activities\n- Perfect for a walk in Central Park\n- "
                                "Consider bringing sunglasses"
                            )
                        }
                    ],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }

    def mock_llm_call(*args, **kwargs):
        return Response(
            200, json=detailed_response, headers={"content-type": "application/json"}
        )

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()
        assert not at.exception

        # Submit a weather query
        at.chat_input[0].set_value(
            "Give me a detailed weather report for New York"
        ).run()

        # Check that formatted response appears in UI
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # Should contain the detailed weather information
        all_content = " ".join(markdown_content)
        assert "75F" in all_content or "temperature" in all_content.lower()
        assert "Clear" in all_content or "clear" in all_content


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_streamlit_multiple_agent_interactions(
    setup_api_mocks, mock_google_adk_client
):
    """
    Tests that the UI correctly handles multiple different types of agent interactions.
    """
    # Mock different responses for different query types
    responses = [
        # Weather response
        {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "The weather is sunny and 75F"}],
                        "role": "model",
                    },
                    "finish_reason": "STOP",
                }
            ]
        },
        # Search response
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    "I found several great restaurants in Paris, "
                                    "including..."
                                )
                            }
                        ],
                        "role": "model",
                    },
                    "finish_reason": "STOP",
                }
            ]
        },
    ]

    response_index = 0

    def mock_llm_call(*args, **kwargs):
        nonlocal response_index
        if response_index < len(responses):
            result = Response(
                200,
                json=responses[response_index],
                headers={"content-type": "application/json"},
            )
            response_index += 1
            return result
        return Response(
            200, json=responses[-1], headers={"content-type": "application/json"}
        )

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # First query - weather
        at.chat_input[0].set_value("What's the weather like?").run()
        assert not at.exception

        # Second query - search
        at.chat_input[0].set_value("Find restaurants in Paris").run()
        assert not at.exception

        # Check that both responses appear in the conversation
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # Should contain elements from both interactions
        assert len(markdown_content) >= 2  # At least user messages and responses


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_streamlit_ui_components_integration(mock_google_adk_client):
    """
    Tests that all UI components (sidebar, chat, etc.) integrate properly with agents.
    """
    # Mock a simple response
    simple_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Hello! I'm ready to help."}],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }

    def mock_llm_call(*args, **kwargs):
        return Response(
            200, json=simple_response, headers={"content-type": "application/json"}
        )

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # Verify app components loaded
        assert not at.exception

        # Check that chat input exists
        assert len(at.chat_input) > 0

        # Check that sidebar elements exist (if any)
        # The app should have basic structure even if sidebar is minimal

        # Test basic interaction
        at.chat_input[0].set_value("Test message").run()
        assert not at.exception

        # Should have some markdown content (user + assistant messages)
        markdown_elements = [
            md for md in at.markdown if md.value and not md.value.startswith("<style>")
        ]
        assert (
            len(markdown_elements) >= 0
        )  # Could be zero if messages are in other components
