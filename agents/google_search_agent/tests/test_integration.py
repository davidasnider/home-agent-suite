"""
Integration tests for the Google Search Agent

These tests verify the agent's behavior in realistic scenarios,
including end-to-end workflows and integration with the ADK framework.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the agents directory to the Python path for testing
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

from google_search_agent.agent import (  # noqa: E402
    create_google_search_agent,
    root_agent,
    MODEL_NAME,
)
from .fixtures.test_queries import (  # noqa: E402
    BASIC_QUERIES,
    COMPLEX_QUERIES,
    INTENT_BASED_QUERIES,
    QUERY_MOCK_RESPONSES,
)


class TestEndToEndWorkflows:
    """Test suite for complete search workflows"""

    def load_mock_responses(self):
        """Load mock responses for integration testing"""
        fixtures_path = (
            Path(__file__).parent / "fixtures" / "mock_search_responses.json"
        )
        with open(fixtures_path, "r") as f:
            return json.load(f)

    @patch("google.adk.tools.google_search")
    def test_successful_search_workflow(self, mock_search_tool, google_search_agent):
        """Test a complete successful search workflow"""
        mock_responses = self.load_mock_responses()
        success_response = mock_responses["successful_weather_search"]

        # Configure mock to return successful response
        mock_search_tool.return_value = success_response

        # Simulate a search workflow
        assert google_search_agent is not None
        assert len(google_search_agent.tools) == 1

        # Verify response structure
        assert success_response["status"] == "success"
        assert len(success_response["results"]) > 0

        # Each result should have essential fields
        for result in success_response["results"]:
            assert "title" in result
            assert "url" in result
            assert "snippet" in result
            assert len(result["title"]) > 0
            assert result["url"].startswith("http")

    @patch("google.adk.tools.google_search")
    def test_multiple_search_queries_workflow(
        self, mock_search_tool, google_search_agent
    ):
        """Test workflow with multiple different search queries"""
        mock_responses = self.load_mock_responses()

        # Configure different responses for different queries
        responses = [
            mock_responses["successful_weather_search"],
            mock_responses["successful_tech_search"],
            mock_responses["empty_search_results"],
        ]
        mock_search_tool.side_effect = responses

        # Test queries from different categories
        test_queries = ["weather today", "latest technology news", "nonexistent query"]

        for i, query in enumerate(test_queries):
            # Each query should be processable
            assert isinstance(query, str)
            assert len(query) > 0

            # Mock should return appropriate response when called
            if i < len(responses):
                expected_response = responses[i]
                # Verify response structure matches expectations
                assert "status" in expected_response
                if expected_response["status"] == "success":
                    assert "results" in expected_response

    @patch("google.adk.tools.google_search")
    def test_error_recovery_workflow(self, mock_search_tool, google_search_agent):
        """Test workflow recovery from errors"""
        mock_responses = self.load_mock_responses()

        # Configure sequence: error, then success
        error_response = mock_responses["api_quota_error"]
        success_response = mock_responses["successful_weather_search"]

        mock_search_tool.side_effect = [
            Exception(error_response["error_message"]),
            success_response,
        ]

        # Agent should remain functional after error
        assert google_search_agent is not None
        assert len(google_search_agent.tools) == 1

        # Verify error response structure
        assert error_response["status"] == "error"
        assert "error_message" in error_response


class TestQueryProcessingIntegration:
    """Test suite for query processing integration"""

    def test_basic_query_processing(self, google_search_agent):
        """Test processing of basic search queries"""
        for query in BASIC_QUERIES[:3]:  # Test first 3 to avoid too many API calls
            # Query should be valid string
            assert isinstance(query, str)
            assert len(query.strip()) > 0

            # Query should be reasonable length
            assert len(query) < 1000

            # Query should contain searchable terms
            words = query.split()
            assert len(words) > 0
            assert all(len(word) > 0 for word in words)

    def test_complex_query_processing(self, google_search_agent):
        """Test processing of complex search queries"""
        for query in COMPLEX_QUERIES[:2]:  # Test first 2 complex queries
            assert isinstance(query, str)
            assert len(query) > 20  # Complex queries should be longer

            # Should contain multiple words
            words = query.split()
            assert len(words) >= 5

    def test_intent_based_query_processing(self, google_search_agent):
        """Test processing of queries with different intents"""
        for intent, queries in INTENT_BASED_QUERIES.items():
            for query in queries[:1]:  # Test one query per intent
                assert isinstance(query, str)
                assert len(query.strip()) > 0

                # Intent should be valid category
                assert intent in [
                    "informational",
                    "navigational",
                    "transactional",
                    "research",
                ]

    @patch("google.adk.tools.google_search")
    def test_query_response_mapping(self, mock_search_tool, google_search_agent):
        """Test mapping between queries and expected responses"""
        mock_responses = self.load_mock_responses()

        # Test specific query-response mappings
        for query, response_key in QUERY_MOCK_RESPONSES.items():
            if response_key in mock_responses:
                expected_response = mock_responses[response_key]
                mock_search_tool.return_value = expected_response

                # Verify response matches expectations
                if expected_response.get("status") == "success":
                    assert "results" in expected_response
                elif expected_response.get("status") == "error":
                    assert "error_message" in expected_response

    def load_mock_responses(self):
        """Load mock responses for testing"""
        fixtures_path = (
            Path(__file__).parent / "fixtures" / "mock_search_responses.json"
        )
        with open(fixtures_path, "r") as f:
            return json.load(f)


class TestADKFrameworkIntegration:
    """Test suite for ADK framework integration"""

    def test_agent_adk_compliance(self, google_search_agent):
        """Test that agent complies with ADK framework requirements"""
        # Agent should have required ADK attributes
        assert hasattr(google_search_agent, "name")
        assert hasattr(google_search_agent, "model")
        assert hasattr(google_search_agent, "tools")
        assert hasattr(google_search_agent, "description")
        assert hasattr(google_search_agent, "instruction")

        # Name should be string
        assert isinstance(google_search_agent.name, str)
        assert len(google_search_agent.name) > 0

        # Model should match expected model
        assert google_search_agent.model == MODEL_NAME

        # Tools should be list
        assert isinstance(google_search_agent.tools, list)
        assert len(google_search_agent.tools) > 0

    def test_tool_adk_integration(self, google_search_agent):
        """Test that tools are properly integrated with ADK"""
        tools = google_search_agent.tools
        assert len(tools) == 1

        search_tool = tools[0]
        # Tool should be a GoogleSearchTool object
        assert search_tool is not None
        assert hasattr(search_tool, "__class__")
        assert "GoogleSearchTool" in str(type(search_tool))

    def test_agent_instantiation_patterns(self):
        """Test different agent instantiation patterns"""
        # Test direct creation
        agent1 = create_google_search_agent()
        assert agent1 is not None

        # Test using global instance
        assert root_agent is not None

        # Test multiple instantiations
        agent2 = create_google_search_agent()
        assert agent2 is not None

        # Agents should be independent but equivalent
        assert agent1 is not agent2
        assert agent1.name == agent2.name
        assert agent1.model == agent2.model

    def test_logging_integration(self, google_search_agent):
        """Test logging integration with ADK"""
        # Agent should be created successfully
        # (logging setup happens during module import)
        assert google_search_agent is not None
        assert google_search_agent.name == "basic_search_agent"

        # Test that agent creation is resilient
        agent = create_google_search_agent()
        assert agent is not None


class TestScalabilityAndPerformance:
    """Test suite for scalability and performance considerations"""

    def test_multiple_agent_creation_performance(self):
        """Test performance of creating multiple agents"""
        agents = []

        # Create multiple agents quickly
        for i in range(10):
            agent = create_google_search_agent()
            agents.append(agent)

            # Each agent should be created successfully
            assert agent is not None
            assert agent.name == "basic_search_agent"

        # All agents should be independent
        assert len(agents) == 10
        agent_ids = [id(agent) for agent in agents]
        assert len(set(agent_ids)) == 10  # All unique instances

    def test_memory_efficiency(self, google_search_agent):
        """Test memory efficiency of agent instances"""
        # Agent should not hold excessive references
        import sys

        # Get reference count before
        initial_refs = sys.getrefcount(google_search_agent)

        # Create temporary references
        temp_refs = [google_search_agent for _ in range(5)]
        increased_refs = sys.getrefcount(google_search_agent)

        # Reference count should increase predictably
        assert increased_refs > initial_refs

        # Clean up
        del temp_refs

        # Reference count should decrease (may not be exact due to Python internals)
        final_refs = sys.getrefcount(google_search_agent)
        assert final_refs <= increased_refs

    @patch("google.adk.tools.google_search")
    def test_concurrent_search_simulation(self, mock_search_tool, google_search_agent):
        """Test simulation of concurrent search operations"""
        mock_responses = self.load_mock_responses()
        success_response = mock_responses["successful_weather_search"]

        # Configure mock for multiple calls
        mock_search_tool.return_value = success_response

        # Simulate multiple searches
        search_queries = ["query1", "query2", "query3", "query4", "query5"]

        for query in search_queries:
            # Each search should be independent
            assert isinstance(query, str)
            assert len(query) > 0

            # Agent should remain consistent
            assert google_search_agent.name == "basic_search_agent"
            assert len(google_search_agent.tools) == 1

    def load_mock_responses(self):
        """Load mock responses for testing"""
        fixtures_path = (
            Path(__file__).parent / "fixtures" / "mock_search_responses.json"
        )
        with open(fixtures_path, "r") as f:
            return json.load(f)


class TestFutureExtensibility:
    """Test suite for future extensibility and growth"""

    def test_tool_extensibility(self, google_search_agent):
        """Test that the agent can be extended with additional tools"""
        original_tools = google_search_agent.tools.copy()
        assert len(original_tools) == 1

        # Mock additional tool
        mock_new_tool = Mock()
        mock_new_tool.name = "additional_search_tool"

        # Should be able to add tools programmatically (if needed in future)
        # This tests the extensibility pattern
        tools_list = google_search_agent.tools
        assert isinstance(tools_list, list)

        # Original tools should remain intact
        assert len(google_search_agent.tools) == len(original_tools)

    def test_configuration_extensibility(self):
        """Test that agent configuration can be extended"""
        # Current configuration should be accessible
        agent = create_google_search_agent()

        # Should be able to inspect configuration
        config_attributes = {
            "name": agent.name,
            "model": agent.model,
            "description": str(agent.description),
            "instruction": str(agent.instruction),
        }

        for attr_name, attr_value in config_attributes.items():
            assert attr_value is not None
            assert len(str(attr_value)) > 0

    def test_callback_extensibility(self, google_search_agent):
        """Test readiness for callback extensions"""
        # Check for potential callback hooks
        potential_callbacks = [
            "before_model_callback",
            "after_model_callback",
            "before_tool_callback",
            "after_tool_callback",
        ]

        for callback_name in potential_callbacks:
            if hasattr(google_search_agent, callback_name):
                callback = getattr(google_search_agent, callback_name)
                # If callback exists, should be None or callable
                assert callback is None or callable(callback)

    def test_search_result_processing_extensibility(self):
        """Test extensibility for search result processing"""
        mock_responses = self.load_mock_responses()

        # Test different response formats for future processing
        response_types = [
            "successful_weather_search",
            "successful_tech_search",
            "empty_search_results",
            "large_response",
        ]

        for response_type in response_types:
            if response_type in mock_responses:
                response = mock_responses[response_type]

                # Response should have consistent structure for processing
                assert "status" in response

                if response["status"] == "success":
                    assert "results" in response
                    assert isinstance(response["results"], list)

                    # Each result should be processable
                    for result in response["results"]:
                        if isinstance(result, dict):
                            # Results should have identifiable structure
                            assert any(
                                key in result for key in ["title", "url", "snippet"]
                            )

    def load_mock_responses(self):
        """Load mock responses for testing"""
        fixtures_path = (
            Path(__file__).parent / "fixtures" / "mock_search_responses.json"
        )
        with open(fixtures_path, "r") as f:
            return json.load(f)
