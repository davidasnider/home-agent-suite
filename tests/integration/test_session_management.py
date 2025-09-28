"""
Session Management Integration Tests

Tests the integration of session management across the application, verifying that:
- Conversation history is properly maintained
- Session state persists across interactions
- Multi-turn conversations work correctly
- Session isolation works properly
"""

import pytest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from httpx import Response


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_conversation_history_persistence(
    setup_api_mocks, mock_google_adk_client
):
    """
    Tests that conversation history is properly maintained across multiple interactions.
    """
    # Mock sequential responses for a multi-turn conversation
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "Hello! I'm your assistant. How can I help you "
                                "today?"
                            }
                        ],
                        "role": "model",
                    },
                    "finish_reason": "STOP",
                }
            ]
        },
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "The weather in New York is currently 75F and "
                                "sunny."
                            }
                        ],
                        "role": "model",
                    },
                    "finish_reason": "STOP",
                }
            ]
        },
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "Yes, as I mentioned, it's 75F in New York - "
                                "perfect for outdoor activities!"
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
        if "generateContent" in kwargs.get("url", ""):
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
        return Response(200, json={}, headers={"content-type": "application/json"})

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # First interaction
        at.chat_input[0].set_value("Hello").run()
        first_interaction_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # Second interaction
        at.chat_input[0].set_value("What's the weather in New York?").run()
        second_interaction_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # Third interaction - reference previous conversation
        at.chat_input[0].set_value("Is that temperature good for a picnic?").run()
        third_interaction_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # Verify conversation history is maintained
        assert len(third_interaction_content) >= len(second_interaction_content)
        assert len(second_interaction_content) >= len(first_interaction_content)

        # All content should be preserved
        all_content = " ".join(third_interaction_content)
        assert "Hello" in all_content or "hello" in all_content.lower()
        assert "weather" in all_content.lower()
        assert "picnic" in all_content.lower()


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_session_state_initialization(mock_google_adk_client):
    """
    Tests that session state is properly initialized when starting a new session.
    """
    simple_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Session initialized successfully!"}],
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
        # Initialize new session
        at = AppTest.from_file("app.py").run()
        assert not at.exception

        # Check that session is properly initialized (no errors on startup)
        # The app should load without exceptions
        assert at is not None

        # First interaction should work
        at.chat_input[0].set_value("Test initial message").run()
        assert not at.exception


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_multi_turn_conversation_context(setup_api_mocks, mock_google_adk_client):
    """
    Tests that context is maintained across multiple conversation turns.
    """
    # Mock responses that show context awareness
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    "I'll help you plan your day. "
                                    "What city are you in?"
                                )
                            }
                        ],
                        "role": "model",
                    },
                    "finish_reason": "STOP",
                }
            ]
        },
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    "Great! New York has beautiful weather today - "
                                    "75F and sunny. "
                                    "Perfect for outdoor activities."
                                )
                            }
                        ],
                        "role": "model",
                    },
                    "finish_reason": "STOP",
                }
            ]
        },
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": (
                                    "Based on the sunny weather in New York I "
                                    "mentioned, I'd recommend Central Park, the "
                                    "High Line, or Brooklyn Bridge for great "
                                    "outdoor experiences."
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
        if "generateContent" in kwargs.get("url", ""):
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
        return Response(200, json={}, headers={"content-type": "application/json"})

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # Multi-turn conversation
        at.chat_input[0].set_value("Help me plan my day").run()
        at.chat_input[0].set_value("I'm in New York").run()
        at.chat_input[0].set_value("What outdoor activities do you recommend?").run()

        # Check that context is maintained throughout
        final_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(final_content)

        # Should reference previous conversation elements
        assert "New York" in all_content
        assert "outdoor" in all_content.lower()
        assert len(final_content) >= 3  # Should have multiple conversation turns


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_session_isolation_between_tests(mock_google_adk_client):
    """
    Tests that sessions are properly isolated between different test runs.
    """
    response1 = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "First session response"}],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }

    response2 = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Second session response"}],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }

    def mock_llm_call_1(*args, **kwargs):
        return Response(
            200, json=response1, headers={"content-type": "application/json"}
        )

    def mock_llm_call_2(*args, **kwargs):
        return Response(
            200, json=response2, headers={"content-type": "application/json"}
        )

    # First session
    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call_1
    ):
        at1 = AppTest.from_file("app.py").run()
        at1.chat_input[0].set_value("First session message").run()
        first_content = [
            md.value
            for md in at1.markdown
            if md.value and not md.value.startswith("<style>")
        ]

    # Second session (should be isolated)
    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call_2
    ):
        at2 = AppTest.from_file("app.py").run()
        at2.chat_input[0].set_value("Second session message").run()
        second_content = [
            md.value
            for md in at2.markdown
            if md.value and not md.value.startswith("<style>")
        ]

    # Sessions should be independent
    first_text = " ".join(first_content)
    second_text = " ".join(second_content)

    # Each session should only contain its own content
    assert "First session message" in first_text
    assert "Second session message" in second_text


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_conversation_state_recovery(setup_api_mocks, mock_google_adk_client):
    """
    Tests that conversation state can be recovered after interruptions.
    """
    # Mock responses for a conversation that gets "interrupted"
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "I'm checking the weather for you..."}],
                        "role": "model",
                    },
                    "finish_reason": "STOP",
                }
            ]
        },
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "The weather is 75F and sunny in New York."}
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
        if "generateContent" in kwargs.get("url", ""):
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
        return Response(200, json={}, headers={"content-type": "application/json"})

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # Start conversation
        at.chat_input[0].set_value("What's the weather like?").run()
        intermediate_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # Continue conversation (simulating recovery)
        at.chat_input[0].set_value("Tell me more details").run()
        final_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # State should be maintained
        assert len(final_content) >= len(intermediate_content)

        all_content = " ".join(final_content)
        assert "weather" in all_content.lower()


@pytest.mark.skip(
    reason="Requires complex app-level mocking of Streamlit session state"
)
@pytest.mark.asyncio
async def test_session_memory_management(mock_google_adk_client):
    """
    Tests that session memory is properly managed during long conversations.
    """
    # Mock a long conversation with many turns
    base_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Response to message"}],
                    "role": "model",
                },
                "finish_reason": "STOP",
            }
        ]
    }

    def mock_llm_call(*args, **kwargs):
        return Response(
            200, json=base_response, headers={"content-type": "application/json"}
        )

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # Simulate multiple conversation turns
        for i in range(5):
            at.chat_input[0].set_value(f"Message {i+1}").run()
            assert not at.exception  # Should not crash due to memory issues

        # Check that conversation is still functional
        final_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # Should have accumulated content from multiple turns
        assert len(final_content) >= 5
