import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
from httpx import Response


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - "
    "use integration tests for component testing"
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
                    "snippet": (
                        "Comprehensive guide to Python programming for beginners "
                        "and experts."
                    ),
                    "link": "https://www.python-guide.org",
                },
                {
                    "title": "Python Official Documentation",
                    "snippet": (
                        "The official Python documentation with tutorials and "
                        "reference materials."
                    ),
                    "link": "https://docs.python.org",
                },
                {
                    "title": "Learn Python - Interactive Tutorial",
                    "snippet": (
                        "Interactive Python tutorial for learning programming "
                        "fundamentals."
                    ),
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
                            "text": (
                                "I found some excellent Python programming resources "
                                "for you:\n\n**1. Python Programming Guide**\n"
                                "Comprehensive guide to Python programming for "
                                "beginners and experts.\n"
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
            200, json=search_response, headers={"content-type": "application/json"}
        )

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()
        at.chat_input[0].set_value("search for python").run()
        assert not at.exception
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)
        assert "Python" in all_content
        assert "Guide" in all_content
