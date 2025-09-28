"""
Search Workflow End-to-End Tests

Tests complete search workflows from user query to final response, verifying that:
- Basic search queries work end-to-end
- Complex search queries are handled properly
- Search results are properly formatted and displayed
- Search error scenarios are handled gracefully
- Multi-step search workflows function correctly
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
async def test_basic_search_workflow_e2e(requests_mock):
    """
    Tests a basic search workflow from query to results display.
    """
    # Mock Google Search API
    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1",
        json={
            "items": [
                {
                    "title": "Python Programming Guide",
                    "snippet": "Comprehensive guide to Python programming for beginners and experts.",
                    "link": "https://www.python-guide.org",
                },
                {
                    "title": "Python Official Documentation",
                    "snippet": "The official Python documentation with tutorials and reference materials.",
                    "link": "https://docs.python.org",
                },
                {
                    "title": "Learn Python - Interactive Tutorial",
                    "snippet": "Interactive Python tutorial for learning programming fundamentals.",
                    "link": "https://www.learnpython.org",
                },
            ]
        },
    )

    # Mock LLM response for search workflow
    search_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": """I found some excellent Python programming resources for you:

**1. Python Programming Guide**
Comprehensive guide to Python programming for beginners and experts.
= https://www.python-guide.org

**2. Python Official Documentation**
The official Python documentation with tutorials and reference materials.
= https://docs.python.org

**3. Learn Python - Interactive Tutorial**
Interactive Python tutorial for learning programming fundamentals.
= https://www.learnpython.org

These resources should give you a great foundation for learning Python programming!"""
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
                200, json=search_response, headers={"content-type": "application/json"}
            )
        return Response(200, json={}, headers={"content-type": "application/json"})

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        # Run the search workflow
        at = AppTest.from_file("app.py").run()

        # Submit search query
        at.chat_input[0].set_value("Find information about Python programming").run()

        # Verify search results are displayed
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should contain search results
        assert "Python" in all_content
        assert "programming" in all_content.lower()
        assert "guide" in all_content.lower() or "tutorial" in all_content.lower()
        assert "python-guide.org" in all_content or "docs.python.org" in all_content


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_location_based_search_workflow_e2e(requests_mock):
    """
    Tests a location-based search workflow (e.g., restaurants, attractions).
    """
    # Mock search results for location-based query
    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1",
        json={
            "items": [
                {
                    "title": "Best Restaurants in Tokyo - Travel Guide",
                    "snippet": "Discover the finest dining experiences in Tokyo, from traditional sushi to modern fusion cuisine.",
                    "link": "https://www.tokyo-restaurants.com",
                },
                {
                    "title": "Tokyo Food Scene - Michelin Guide",
                    "snippet": "Michelin-starred restaurants and hidden gems in Tokyo's diverse culinary landscape.",
                    "link": "https://www.michelin-tokyo.com",
                },
                {
                    "title": "Authentic Tokyo Dining Experiences",
                    "snippet": "Local recommendations for authentic Japanese dining in Tokyo neighborhoods.",
                    "link": "https://www.authentic-tokyo.com",
                },
            ]
        },
    )

    # Mock LLM response for location search
    location_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": """Here are the best restaurant options I found for Tokyo:

🍣 **Best Restaurants in Tokyo - Travel Guide**
Discover the finest dining experiences in Tokyo, from traditional sushi to modern fusion cuisine.

⭐ **Tokyo Food Scene - Michelin Guide**
Michelin-starred restaurants and hidden gems in Tokyo's diverse culinary landscape.

🏮 **Authentic Tokyo Dining Experiences**
Local recommendations for authentic Japanese dining in Tokyo neighborhoods.

Tokyo offers an incredible range of dining options from street food to world-class restaurants!"""
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
                200,
                json=location_response,
                headers={"content-type": "application/json"},
            )
        return Response(200, json={}, headers={"content-type": "application/json"})

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # Location-based search query
        at.chat_input[0].set_value("Find the best restaurants in Tokyo").run()

        # Verify location search results
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should contain location-specific results
        assert "Tokyo" in all_content
        assert "restaurants" in all_content.lower()
        assert "sushi" in all_content.lower() or "japanese" in all_content.lower()
        assert "michelin" in all_content.lower() or "dining" in all_content.lower()


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_multi_step_search_workflow_e2e(requests_mock):
    """
    Tests a multi-step search workflow with refinement and follow-up queries.
    """
    # Mock different search results for each step
    call_count = 0

    def search_callback(request, context):
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            # First search: general results
            return {
                "items": [
                    {
                        "title": "Travel Guide to Italy",
                        "snippet": "Complete travel guide covering all major Italian destinations.",
                        "link": "https://www.italy-guide.com",
                    }
                ]
            }
        else:
            # Second search: more specific results
            return {
                "items": [
                    {
                        "title": "Rome Travel Tips - Best Attractions",
                        "snippet": "Essential Rome attractions including Colosseum, Vatican, and hidden gems.",
                        "link": "https://www.rome-attractions.com",
                    },
                    {
                        "title": "Rome Food and Culture Guide",
                        "snippet": "Authentic Roman cuisine and cultural experiences for travelers.",
                        "link": "https://www.rome-culture.com",
                    },
                ]
            }

    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1", json=search_callback
    )

    # Mock responses for multi-step search
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "I found a general travel guide for Italy. Would you like me to search for more specific information about particular cities or regions?"
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
                                "text": "Perfect! Here are specific Rome travel resources:\n\n**Rome Travel Tips - Best Attractions**: Essential Rome attractions including Colosseum, Vatican, and hidden gems.\n\n**Rome Food and Culture Guide**: Authentic Roman cuisine and cultural experiences for travelers."
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

        # Multi-step search workflow
        at.chat_input[0].set_value("Find travel information about Italy").run()
        at.chat_input[0].set_value(
            "Can you find more specific information about Rome?"
        ).run()

        # Verify multi-step search progression
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should show progression from general to specific
        assert "Italy" in all_content
        assert "Rome" in all_content
        assert "Colosseum" in all_content or "Vatican" in all_content
        assert "attractions" in all_content.lower() or "culture" in all_content.lower()


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_search_with_no_results_workflow_e2e(requests_mock):
    """
    Tests search workflow when no results are found.
    """
    # Mock empty search results
    requests_mock.get("https://www.googleapis.com/customsearch/v1", json={"items": []})

    # Mock LLM response for no results
    no_results_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "I couldn't find any results for 'xyzveryuncommonquerythatreturnsnothing'. This might be because:\n\n• The search term is too specific\n• There might be a typo in the query\n• The information might not be widely available online\n\nWould you like to try a different search term or rephrase your query?"
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
                200,
                json=no_results_response,
                headers={"content-type": "application/json"},
            )
        return Response(200, json={}, headers={"content-type": "application/json"})

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # Search for something unlikely to have results
        at.chat_input[0].set_value(
            "Find information about xyzveryuncommonquerythatreturnsnothing"
        ).run()

        # Verify no results handling
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should handle no results gracefully
        assert (
            "no results" in all_content.lower()
            or "couldn't find" in all_content.lower()
        )
        assert "try" in all_content.lower() or "rephrase" in all_content.lower()


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_search_error_handling_workflow_e2e(requests_mock):
    """
    Tests search workflow when API errors occur.
    """
    # Mock search API error
    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1",
        status_code=403,
        json={"error": {"message": "Quota exceeded"}},
    )

    # Mock LLM response for search error
    error_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "I'm sorry, I'm currently unable to perform web searches due to a service limitation. This might be due to:\n\n• API quota limits\n• Temporary service issues\n• Network connectivity problems\n\nPlease try again later, or let me know if there's another way I can help you!"
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
                200, json=error_response, headers={"content-type": "application/json"}
            )
        return Response(200, json={}, headers={"content-type": "application/json"})

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # Attempt search that will encounter API error
        at.chat_input[0].set_value("Search for the latest technology news").run()

        # Verify error handling
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should handle API errors gracefully
        assert "sorry" in all_content.lower() or "unable" in all_content.lower()
        assert "service" in all_content.lower() or "try again" in all_content.lower()
        assert not at.exception  # Should not crash the app


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_search_result_formatting_workflow_e2e(requests_mock):
    """
    Tests that search results are properly formatted in the UI.
    """
    # Mock rich search results
    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1",
        json={
            "items": [
                {
                    "title": "Machine Learning Tutorial - Complete Guide",
                    "snippet": "Comprehensive machine learning tutorial covering algorithms, implementation, and real-world applications with Python examples.",
                    "link": "https://www.ml-tutorial.com",
                    "displayLink": "ml-tutorial.com",
                },
                {
                    "title": "Deep Learning with TensorFlow",
                    "snippet": "Learn deep learning fundamentals using TensorFlow and Keras for neural network development.",
                    "link": "https://www.tensorflow-guide.com",
                    "displayLink": "tensorflow-guide.com",
                },
            ]
        },
    )

    # Mock well-formatted LLM response
    formatted_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": """Here are the top machine learning resources I found:

## > Machine Learning Tutorial - Complete Guide
**Source**: ml-tutorial.com
Comprehensive machine learning tutorial covering algorithms, implementation, and real-world applications with Python examples.
[View Resource →](https://www.ml-tutorial.com)

## 🧠 Deep Learning with TensorFlow
**Source**: tensorflow-guide.com
Learn deep learning fundamentals using TensorFlow and Keras for neural network development.
[View Resource →](https://www.tensorflow-guide.com)

These resources provide both theoretical foundations and practical implementation examples for machine learning!"""
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
                200,
                json=formatted_response,
                headers={"content-type": "application/json"},
            )
        return Response(200, json={}, headers={"content-type": "application/json"})

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()

        # Search query for well-formatted results
        at.chat_input[0].set_value("Find machine learning tutorials").run()

        # Verify result formatting
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should contain well-formatted results
        assert "Machine Learning" in all_content
        assert "TensorFlow" in all_content
        assert "tutorial" in all_content.lower() or "guide" in all_content.lower()
        assert "ml-tutorial.com" in all_content or "tensorflow-guide.com" in all_content
        assert "algorithms" in all_content.lower() or "python" in all_content.lower()


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_search_query_refinement_workflow_e2e(requests_mock):
    """
    Tests workflow where search queries are refined based on initial results.
    """
    # Mock progressive search refinement
    call_count = 0

    def search_callback(request, context):
        nonlocal call_count
        call_count += 1

        if call_count == 1:
            # Broad initial search
            return {
                "items": [
                    {
                        "title": "Cooking Basics - General Guide",
                        "snippet": "General cooking tips and basic techniques for beginners.",
                        "link": "https://www.cooking-basics.com",
                    }
                ]
            }
        else:
            # Refined search
            return {
                "items": [
                    {
                        "title": "Italian Pasta Recipes - Authentic Collection",
                        "snippet": "Traditional Italian pasta recipes with step-by-step instructions and ingredient guides.",
                        "link": "https://www.italian-pasta.com",
                    },
                    {
                        "title": "Perfect Pasta Cooking Techniques",
                        "snippet": "Master the art of cooking pasta with professional tips and timing guides.",
                        "link": "https://www.pasta-techniques.com",
                    },
                ]
            }

    requests_mock.get(
        "https://www.googleapis.com/customsearch/v1", json=search_callback
    )

    # Mock refinement responses
    responses = [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "I found some general cooking information. Would you like me to search for something more specific, like a particular cuisine or dish type?"
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
                                "text": "Perfect! Here are specific Italian pasta resources:\n\n**Italian Pasta Recipes**: Traditional recipes with step-by-step instructions.\n**Perfect Pasta Cooking Techniques**: Professional tips and timing guides.\n\nThese should give you everything you need for authentic Italian pasta!"
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

        # Search refinement workflow
        at.chat_input[0].set_value("Find cooking information").run()
        at.chat_input[0].set_value(
            "I'm specifically interested in Italian pasta recipes"
        ).run()

        # Verify query refinement
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)

        # Should show progression from general to specific
        assert "cooking" in all_content.lower()
        assert "Italian" in all_content
        assert "pasta" in all_content.lower()
        assert "recipes" in all_content.lower() or "techniques" in all_content.lower()
