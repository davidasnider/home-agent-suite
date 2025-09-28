from streamlit.testing.v1 import AppTest
from unittest import mock
from httpx import Response


@mock.patch("google.genai._api_client.AsyncHttpxClient.request")
def test_weather_workflow_e2e(mock_request, requests_mock):
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

    # Simple text response that should work with the Google ADK
    simple_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "The weather in New York is 75F today "
                                "with sunny skies."
                            )
                        }
                    ],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }

    # Configure the mock to return these responses in order on each call
    # Create proper httpx Response objects with correct headers
    def mock_llm_call(*args, **kwargs):
        """Mock LLM calls to return a predefined weather response"""
        # Check if this is a generateContent request
        if "generateContent" in kwargs.get("url", ""):
            # Look at the request content to understand what the LLM is being asked
            if "content" in kwargs:
                try:
                    import json

                    request_data = json.loads(kwargs["content"])
                    if "contents" in request_data:
                        # Check if this appears to be a request that contains
                        # weather-related text
                        last_content = (
                            request_data["contents"][-1]
                            if request_data["contents"]
                            else {}
                        )
                        if "parts" in last_content:
                            for part in last_content["parts"]:
                                if "text" in part and "weather" in part["text"].lower():
                                    # Return our predefined weather response
                                    return Response(
                                        200,
                                        json=simple_response,
                                        headers={"content-type": "application/json"},
                                    )
                except Exception:
                    pass

        # Default response for all other requests
        return Response(
            200, json=simple_response, headers={"content-type": "application/json"}
        )

    mock_request.side_effect = mock_llm_call

    # 2. Run the Streamlit app using AppTest
    at = AppTest.from_file("app.py").run()

    # 3. Interact with the app
    at.chat_input[0].set_value("What's the weather like in New York?").run()

    # 4. Assert the expected weather response is in the UI
    # Look for our mocked response text in the chat interface
    weather_responses = [
        md.value for md in at.markdown if "75F today with sunny skies" in md.value
    ]

    available_markdown = [
        md.value
        for md in at.markdown
        if not md.value.startswith("<style>") and not md.value.startswith("---")
    ]
    assert len(weather_responses) > 0, (
        f"Expected weather response not found in UI. "
        f"Available markdown: {available_markdown}"
    )
    assert (
        "The weather in New York is 75F today with sunny skies." in weather_responses[0]
    )

    # Verify the mock was called, confirming LLM calls were intercepted
    assert mock_request.call_count >= 1, (
        f"Mock should have been called at least once, "
        f"was called {mock_request.call_count} times"
    )
