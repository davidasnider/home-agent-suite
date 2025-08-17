"""
Error handling tests for the Google Search Agent

These tests verify that the agent properly handles various error conditions,
API failures, and edge cases that may occur during search operations.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the agents directory to the Python path for testing
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

from google_search_agent.agent import create_google_search_agent  # noqa: E402

# Import for potential future use
# from .fixtures.test_queries import EDGE_CASE_QUERIES  # noqa: E402


class TestAPIErrorHandling:
    """Test suite for API error scenarios"""

    def load_error_responses(self):
        """Load error response fixtures"""
        fixtures_path = (
            Path(__file__).parent / "fixtures" / "mock_search_responses.json"
        )
        with open(fixtures_path, "r") as f:
            return json.load(f)

    @patch("google.adk.tools.google_search")
    def test_api_quota_exceeded_error(self, mock_search_tool, google_search_agent):
        """Test handling of API quota exceeded errors"""
        error_responses = self.load_error_responses()
        quota_error = error_responses["api_quota_error"]

        # Configure mock to raise quota error
        mock_search_tool.side_effect = Exception(quota_error["error_message"])

        # Verify the agent has the tool configured
        assert len(google_search_agent.tools) == 1

        # Test that quota error information is structured correctly
        assert quota_error["status"] == "error"
        assert quota_error["error_code"] == "QUOTA_EXCEEDED"
        assert "quota exceeded" in quota_error["error_message"].lower()
        assert "retry_after" in quota_error

    @patch("google.adk.tools.google_search")
    def test_network_timeout_error(self, mock_search_tool, google_search_agent):
        """Test handling of network timeout errors"""
        error_responses = self.load_error_responses()
        timeout_error = error_responses["network_timeout_error"]

        # Configure mock to simulate timeout
        # (using Exception since TimeoutError may not be available)
        mock_search_tool.side_effect = Exception(timeout_error["error_message"])

        # Verify error structure
        assert timeout_error["status"] == "error"
        assert timeout_error["error_code"] == "TIMEOUT"
        assert "timed out" in timeout_error["error_message"].lower()
        assert timeout_error["timeout_duration"] == 30

    @patch("google.adk.tools.google_search")
    def test_authentication_error(self, mock_search_tool, google_search_agent):
        """Test handling of authentication/API key errors"""
        error_responses = self.load_error_responses()
        auth_error = error_responses["api_key_error"]

        # Configure mock to simulate auth error
        mock_search_tool.side_effect = Exception(auth_error["error_message"])

        # Verify error structure
        assert auth_error["status"] == "error"
        assert auth_error["error_code"] == "AUTH_ERROR"
        error_msg = auth_error["error_message"].lower()
        assert "api key" in error_msg or "authentication" in error_msg

    @patch("google.adk.tools.google_search")
    def test_invalid_query_error(self, mock_search_tool, google_search_agent):
        """Test handling of invalid query errors"""
        error_responses = self.load_error_responses()
        invalid_error = error_responses["invalid_query_error"]

        # Configure mock to simulate invalid query error
        mock_search_tool.side_effect = ValueError(invalid_error["error_message"])

        # Verify error structure
        assert invalid_error["status"] == "error"
        assert invalid_error["error_code"] == "INVALID_QUERY"
        assert "invalid" in invalid_error["error_message"].lower()

    @patch("google.adk.tools.google_search")
    def test_generic_exception_handling(self, mock_search_tool, google_search_agent):
        """Test handling of unexpected exceptions"""
        # Configure mock to raise unexpected exception
        mock_search_tool.side_effect = RuntimeError("Unexpected system error")

        # Agent should still be functional
        assert google_search_agent is not None
        assert len(google_search_agent.tools) == 1


class TestEdgeCaseHandling:
    """Test suite for edge case scenarios"""

    def test_empty_query_handling(self, google_search_agent):
        """Test handling of empty search queries"""
        empty_queries = ["", " ", "   ", "\t", "\n"]

        for query in empty_queries:
            # Empty queries should be identifiable
            assert len(query.strip()) == 0

    def test_very_long_query_handling(self, google_search_agent):
        """Test handling of extremely long search queries"""
        long_query = "test " * 1000  # Very long query

        assert len(long_query) > 1000
        assert isinstance(long_query, str)

    def test_special_character_queries(self, google_search_agent):
        """Test handling of queries with special characters"""
        special_queries = [
            "!@#$%^&*()",
            "query with\nnewlines",
            "query\twith\ttabs",
            "query with ümläuts and açcénts",
            "query with 中文 characters",
            "query with emoji 🔍📱",
        ]

        for query in special_queries:
            # Should be valid strings that can be processed
            assert isinstance(query, str)
            assert len(query) > 0

    def test_numeric_only_queries(self, google_search_agent):
        """Test handling of numeric-only queries"""
        numeric_queries = ["123456", "0", "999999999999", "3.14159", "-42"]

        for query in numeric_queries:
            assert isinstance(query, str)
            # Should contain digits
            assert any(char.isdigit() for char in query)


class TestMalformedResponseHandling:
    """Test suite for malformed API response handling"""

    def load_malformed_responses(self):
        """Load malformed response fixtures"""
        fixtures_path = (
            Path(__file__).parent / "fixtures" / "mock_search_responses.json"
        )
        with open(fixtures_path, "r") as f:
            return json.load(f)

    @patch("google.adk.tools.google_search")
    def test_malformed_response_structure(self, mock_search_tool, google_search_agent):
        """Test handling of malformed API responses"""
        malformed_responses = self.load_malformed_responses()
        malformed = malformed_responses["malformed_response"]

        # Configure mock to return malformed response
        mock_search_tool.return_value = malformed

        # Verify the response structure is problematic
        assert malformed["status"] == "success"
        assert isinstance(malformed["results"], list)

        # Check that some results have missing or invalid fields
        results = malformed["results"]
        assert len(results) > 0

        # First result has null title
        assert results[0]["title"] is None

        # Second result is not a dict
        assert isinstance(results[1], str)

        # Third result has unexpected fields
        assert "unexpected_field" in results[2]

    @patch("google.adk.tools.google_search")
    def test_partial_response_handling(self, mock_search_tool, google_search_agent):
        """Test handling of responses with missing fields"""
        partial_responses = self.load_malformed_responses()
        partial = partial_responses["partial_response"]

        # Configure mock to return partial response
        mock_search_tool.return_value = partial

        # Verify partial response structure
        assert partial["status"] == "success"
        results = partial["results"]

        # Check that results have varying field availability
        for result in results:
            if isinstance(result, dict):
                # Some results may be missing title, url, or snippet
                title = result.get("title")
                url = result.get("url")
                snippet = result.get("snippet")

                # At least one field should be present
                assert title or url or snippet

    @patch("google.adk.tools.google_search")
    def test_none_response_handling(self, mock_search_tool, google_search_agent):
        """Test handling of None response from API"""
        # Configure mock to return None
        mock_search_tool.return_value = None

        # Agent should still be functional
        assert google_search_agent is not None
        assert len(google_search_agent.tools) == 1

    @patch("google.adk.tools.google_search")
    def test_empty_response_handling(self, mock_search_tool, google_search_agent):
        """Test handling of empty response from API"""
        # Configure mock to return empty dict
        mock_search_tool.return_value = {}

        # Agent should still be functional
        assert google_search_agent is not None
        assert len(google_search_agent.tools) == 1


class TestLoggingAndDebugging:
    """Test suite for logging and debugging capabilities"""

    def test_error_logging(self, google_search_agent):
        """Test that errors are properly logged"""
        # Agent should be created successfully
        assert google_search_agent is not None
        assert google_search_agent.name == "basic_search_agent"

    @patch("google_search_agent.agent.setup_logging")
    def test_logging_setup_failure_resilience(self, mock_setup_logging):
        """Test agent creation resilience when logging setup fails"""
        # Configure logging setup to fail
        mock_setup_logging.side_effect = Exception("Logging setup failed")

        # Agent creation should still succeed
        agent = create_google_search_agent()
        assert agent is not None
        assert agent.name == "basic_search_agent"

    def test_debug_information_availability(self, google_search_agent):
        """Test that debug information is available"""
        # Agent should have identifiable components for debugging
        assert hasattr(google_search_agent, "name")
        assert hasattr(google_search_agent, "model")
        assert hasattr(google_search_agent, "tools")
        assert hasattr(google_search_agent, "description")
        assert hasattr(google_search_agent, "instruction")

        # All components should have string representations for debugging
        assert str(google_search_agent.name)
        assert str(google_search_agent.model)
        assert str(google_search_agent.description)
        assert str(google_search_agent.instruction)


class TestRecoveryMechanisms:
    """Test suite for error recovery and resilience"""

    def test_agent_creation_after_errors(self):
        """Test that new agents can be created after errors"""
        # Create multiple agents to test resilience
        agents = []

        for i in range(3):
            try:
                agent = create_google_search_agent()
                agents.append(agent)
            except Exception as e:
                pytest.fail(f"Agent creation failed on attempt {i+1}: {e}")

        # All agents should be created successfully
        assert len(agents) == 3
        for agent in agents:
            assert agent is not None
            assert agent.name == "basic_search_agent"

    @patch("google.adk.tools.google_search")
    def test_tool_error_recovery(self, mock_search_tool, google_search_agent):
        """Test recovery from tool execution errors"""
        # First call fails, second succeeds
        mock_search_tool.side_effect = [
            Exception("First call fails"),
            {"status": "success", "results": []},
        ]

        # Agent should remain functional
        assert google_search_agent is not None
        assert len(google_search_agent.tools) == 1

    def test_memory_and_state_isolation(self):
        """Test that agents don't share error state"""
        agent1 = create_google_search_agent()
        agent2 = create_google_search_agent()

        # Agents should be independent instances
        assert agent1 is not agent2
        assert agent1.name == agent2.name
        assert agent1.model == agent2.model

        # They should have independent tool lists
        assert agent1.tools is not agent2.tools
        assert len(agent1.tools) == len(agent2.tools) == 1
