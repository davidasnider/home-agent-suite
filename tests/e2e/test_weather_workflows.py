import pytest
from streamlit.testing.v1 import AppTest
from unittest import mock
from httpx import Response, AsyncClient

@mock.patch.object(AsyncClient, "post")
def test_weather_workflow_e2e(mock_post, requests_mock):
    """
    Tests a simple end-to-end weather workflow using AppTest.
    """
    # 1. Mock the external APIs

    # Mock the Tomorrow.io API response
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        json={
            "timelines": {
                "hourly": [
                    {
                        "time": "2025-09-27T14:00:00Z",
                        "values": {"temperature": 75},
                    }
                ]
            }
        },
    )

    # Define the sequence of responses the mock LLM will return.
    tool_call_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"function_call": {"name": "get_tmrw_weather_tool", "args": {"location": "New York"}}}],
                    "role": "model",
                },
                "finish_reason": "TOOL_CALLS",
            }
        ]
    }

    final_answer_response = {
        "candidates": [
            {
                "content": {"parts": [{"text": "The weather in New York is 75F."}], "role": "model"},
                "finish_reason": "STOP",
            }
        ]
    }

    # Configure the mock to return these responses in order on each call
    mock_post.side_effect = [
        Response(200, json=tool_call_response),
        Response(200, json=final_answer_response),
    ]

    # 2. Run the Streamlit app using AppTest
    at = AppTest.from_file("app.py").run()

    # 3. Interact with the app
    at.chat_input[0].set_value("What's the weather like in New York?").run()

    # 4. Assert the final response is in the UI
    assert "The weather in New York is 75F." in at.markdown[len(at.markdown)-1].value
    assert mock_post.call_count == 2