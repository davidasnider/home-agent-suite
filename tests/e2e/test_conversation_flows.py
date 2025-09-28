"""
Conversation Flow End-to-End Tests

Tests complete conversation flows from user input to final response, verifying that:
- Multi-turn conversations work correctly
- Context is maintained across conversation turns
- Different types of conversations (weather, search, mixed) work properly
- Complex conversational scenarios are handled correctly
"""

import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import Mock, patch
from httpx import Response
import json


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_weather_conversation_flow_e2e(requests_mock):
    """
    Tests a complete weather-focused conversation flow end-to-end.
    """
    # Mock Tomorrow.io API
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        json={
            "timelines": {
                "hourly": [
                    {
                        "time": "2025-09-28T14:00:00Z",
                        "values": {
                            "temperature": 75,
                            "humidity": 65,
                            "windSpeed": 8.5,
                            "weatherCode": 1000,
                            "precipitationProbability": 10,
                        },
                    }
                ]
            }
        },
    )

    # Mock sequential LLM responses for a weather conversation
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "Hello! I'd be happy to help you with weather information. What location are you interested in?"
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
                                "text": "The current weather in New York is 75F with clear skies and light winds at 8.5 mph. Perfect weather for outdoor activities!"
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
                                "text": "With the beautiful 75F weather and clear skies in New York, I'd recommend Central Park for a walk, outdoor dining, or visiting the High Line. The low humidity (65%) makes it very comfortable!"
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
        # Start the conversation
        at = AppTest.from_file("app.py").run()

        # Turn 1: Initial greeting
        at.chat_input[0].set_value("Hi, I need weather information").run()

        # Turn 2: Specific location request
        at.chat_input[0].set_value("What's the weather like in New York?").run()

        # Turn 3: Follow-up question using context
        at.chat_input[0].set_value("What outdoor activities would you recommend?").run()

        # Verify the conversation flow
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should contain elements from all conversation turns
        assert "weather" in all_content.lower()
        assert "New York" in all_content or "new york" in all_content.lower()
        assert "outdoor" in all_content.lower() or "activities" in all_content.lower()
        assert "75" in all_content or "temperature" in all_content.lower()

        # Should have multiple conversation turns
        assert len(markdown_content) >= 3


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_search_conversation_flow_e2e(requests_mock):
    """
    Tests a complete search-focused conversation flow end-to-end.
    """
    # Mock Google Search API
    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1",
        json={
            "items": [
                {
                    "title": "Best Restaurants in Paris - Travel Guide",
                    "snippet": "Discover the finest dining experiences in Paris, from Michelin-starred establishments to cozy bistros.",
                    "link": "https://www.travel-guide.com/paris-restaurants",
                },
                {
                    "title": "Top 10 Must-Try Restaurants in Paris",
                    "snippet": "A curated list of exceptional restaurants in the City of Light, featuring French cuisine and international flavors.",
                    "link": "https://www.foodie-guide.com/paris",
                },
            ]
        },
    )

    # Mock sequential LLM responses for a search conversation
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "I'd be happy to help you find information! What would you like to search for?"
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
                                "text": "I found some excellent restaurant recommendations for Paris! Here are the top results:\n\n1. **Best Restaurants in Paris - Travel Guide**: Discover the finest dining experiences in Paris, from Michelin-starred establishments to cozy bistros.\n\n2. **Top 10 Must-Try Restaurants in Paris**: A curated list of exceptional restaurants in the City of Light."
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
                                "text": "Based on the restaurants I found earlier, I'd specifically recommend looking for Michelin-starred establishments for special occasions, or cozy bistros for a more authentic Parisian experience. French cuisine is obviously a must-try!"
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

        # Turn 1: Initial search request
        at.chat_input[0].set_value("Help me find information").run()

        # Turn 2: Specific search query
        at.chat_input[0].set_value("Find the best restaurants in Paris").run()

        # Turn 3: Follow-up question referencing previous results
        at.chat_input[0].set_value(
            "What type of cuisine would you recommend from those results?"
        ).run()

        # Verify the search conversation flow
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should contain search-related content
        assert "restaurants" in all_content.lower() or "paris" in all_content.lower()
        assert "search" in all_content.lower() or "find" in all_content.lower()
        assert "michelin" in all_content.lower() or "cuisine" in all_content.lower()


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_mixed_conversation_flow_e2e(requests_mock):
    """
    Tests a conversation that involves both weather and search queries.
    """
    # Mock both APIs
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        json={
            "timelines": {
                "hourly": [
                    {
                        "time": "2025-09-28T14:00:00Z",
                        "values": {"temperature": 68, "weatherCode": 1001},  # Cloudy
                    }
                ]
            }
        },
    )

    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1",
        json={
            "items": [
                {
                    "title": "Indoor Activities in Paris",
                    "snippet": "Great indoor attractions for cloudy days in Paris including museums, galleries, and shopping.",
                    "link": "https://www.paris-indoor.com",
                }
            ]
        },
    )

    # Mock responses for mixed conversation
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "The weather in Paris is currently 68F and cloudy. It might be a good day for indoor activities."
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
                                "text": "I found some great indoor activities for the cloudy weather in Paris! Here are some recommendations:\n\n**Indoor Activities in Paris**: Great indoor attractions for cloudy days including museums, galleries, and shopping.\n\nPerfect for today's 68F cloudy weather!"
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

        # Mixed conversation: weather then search
        at.chat_input[0].set_value("What's the weather like in Paris?").run()
        at.chat_input[0].set_value(
            "Given that weather, what indoor activities would you recommend?"
        ).run()

        # Verify mixed conversation handles both domains
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should contain both weather and search elements
        assert "68" in all_content or "cloudy" in all_content.lower()
        assert "indoor" in all_content.lower() or "activities" in all_content.lower()
        assert "paris" in all_content.lower()


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_context_preservation_across_turns_e2e(requests_mock):
    """
    Tests that context is preserved across multiple conversation turns.
    """
    # Mock APIs
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        json={
            "timelines": {
                "hourly": [
                    {
                        "time": "2025-09-28T14:00:00Z",
                        "values": {"temperature": 82, "weatherCode": 1000},
                    }
                ]
            }
        },
    )

    # Mock responses that demonstrate context awareness
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "The weather in Miami is currently 82F and sunny - perfect beach weather!"
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
                                "text": "Given the hot 82F sunny weather in Miami I mentioned, I'd definitely recommend bringing sunscreen, plenty of water, and lightweight clothing. Perfect day for the beach!"
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
                                "text": "Since we established Miami is sunny and 82F today, for outdoor activities I'd suggest South Beach, Bayfront Park, or a boat tour. The weather is ideal for being outside!"
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

        # Progressive conversation building on previous context
        at.chat_input[0].set_value("What's the weather in Miami?").run()
        at.chat_input[0].set_value("What should I bring for that weather?").run()
        at.chat_input[0].set_value("What outdoor activities would be good?").run()

        # Verify context preservation
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should reference previous context in later responses
        assert "Miami" in all_content
        assert "82" in all_content
        assert "sunny" in all_content.lower()
        assert "sunscreen" in all_content.lower() or "water" in all_content.lower()
        assert "beach" in all_content.lower() or "outdoor" in all_content.lower()


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_error_recovery_in_conversation_e2e(requests_mock):
    """
    Tests that conversations can recover from errors and continue normally.
    """
    # Mock API with initial error then success
    call_count = 0

    def api_callback(request, context):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First call fails
            context.status_code = 500
            return "Internal Server Error"
        else:
            # Subsequent calls succeed
            return {
                "timelines": {
                    "hourly": [
                        {
                            "time": "2025-09-28T14:00:00Z",
                            "values": {"temperature": 70, "weatherCode": 1000},
                        }
                    ]
                }
            }

    requests_mock.get("https://api.tomorrow.io/v4/weather/forecast", json=api_callback)

    # Mock responses showing error recovery
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "I'm sorry, I'm having trouble accessing the weather service right now. Please try again."
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
                                "text": "Great! Now I can access the weather data. The weather in Boston is 70F and sunny. Much better!"
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

        # First attempt (should encounter error)
        at.chat_input[0].set_value("What's the weather in Boston?").run()

        # Second attempt (should succeed)
        at.chat_input[0].set_value("Can you try checking the weather again?").run()

        # Verify error recovery
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should show both error and recovery
        assert "trouble" in all_content.lower() or "sorry" in all_content.lower()
        assert "70" in all_content or "Boston" in all_content


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_long_conversation_flow_e2e(requests_mock):
    """
    Tests a longer conversation with multiple topics and turns.
    """
    # Mock APIs for multiple different requests
    requests_mock.get(
        "https://api.tomorrow.io/v4/weather/forecast",
        json={
            "timelines": {
                "hourly": [
                    {
                        "time": "2025-09-28T14:00:00Z",
                        "values": {"temperature": 73, "weatherCode": 1000},
                    }
                ]
            }
        },
    )

    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1",
        json={
            "items": [
                {
                    "title": "Seattle Coffee Shops",
                    "snippet": "Best coffee shops in Seattle for every taste and budget.",
                    "link": "https://www.seattle-coffee.com",
                }
            ]
        },
    )

    # Mock extended conversation responses
    base_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "I'm here to help with weather and search queries!"}
                    ],
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

        # Extended conversation with multiple topics
        conversation_turns = [
            "Hello, I'm planning a trip",
            "What's the weather like in Seattle?",
            "That sounds nice for walking around",
            "Can you find coffee shops in Seattle?",
            "Which ones are best for working?",
            "Thanks for the help!",
        ]

        for turn in conversation_turns:
            at.chat_input[0].set_value(turn).run()
            assert not at.exception  # Should not crash during long conversation

        # Verify long conversation handling
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]

        # Should accumulate content from all turns
        assert len(markdown_content) >= len(conversation_turns)

        # Should handle the conversation gracefully
        all_content = " ".join(markdown_content)
        assert len(all_content) > 0
