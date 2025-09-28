import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
from httpx import Response


@pytest.mark.skip(
    reason="E2E tests require complex app-level mocking - "
    "use integration tests for component testing"
)
@pytest.mark.asyncio
async def test_paris_restaurant_recommendations(requests_mock):
    """
    Tests a simple conversation flow for restaurant recommendations.
    """
    # Mock LLM response
    llm_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "I found some excellent restaurant recommendations for "
                                "Paris! Here are the top results:\n\n"
                                "1. **Best Restaurants in Paris - Travel Guide**: "
                                "Discover the finest dining experiences in Paris, "
                                "from Michelin-starred establishments to cozy bistros."
                                "\n\n2. **Top 10 Must-Try Restaurants in Paris**: "
                                "A curated list of exceptional restaurants in the "
                                "City of Light."
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
            200, json=llm_response, headers={"content-type": "application/json"}
        )

    with patch(
        "google.genai._api_client.AsyncHttpxClient.request", side_effect=mock_llm_call
    ):
        at = AppTest.from_file("app.py").run()
        at.chat_input[0].set_value("restaurants in Paris").run()
        assert not at.exception
        markdown_content = [
            md.value
            for md in at.markdown
            if md.value and not md.value.startswith("<style>")
        ]
        all_content = " ".join(markdown_content)
        assert "Paris" in all_content
        assert "Best Restaurants" in all_content
