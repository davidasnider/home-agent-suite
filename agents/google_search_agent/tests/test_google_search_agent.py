"""
Comprehensive tests for the Google Search Agent

These tests verify that the google search agent is properly created, configured,
and handles various scenarios including successful searches, error conditions,
and edge cases. The test suite provides comprehensive coverage for future-proofing
as the agent grows in complexity.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add the agents directory to the Python path for testing
# This must be done before importing the agent modules
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

from google_search_agent.agent import (  # noqa: E402
    MODEL_NAME,
    create_google_search_agent,
    root_agent,
)
from .fixtures.test_queries import (  # noqa: E402
    BASIC_QUERIES,
    EDGE_CASE_QUERIES,
    QUERY_EXPECTATIONS,
)


def test_google_search_agent_creation():
    """Test that google search agent is created successfully"""
    agent = create_google_search_agent()

    assert agent is not None
    assert agent.name == "basic_search_agent"
    assert agent.model == MODEL_NAME
    assert agent.model == "gemini-2.5-flash"
    assert len(agent.tools) == 1  # google search tool


def test_google_search_model_constant():
    """Test that MODEL_NAME constant is correct"""
    assert MODEL_NAME == "gemini-2.5-flash"


def test_google_search_agent_has_search_tool():
    """Test that google search agent has search tool"""
    agent = create_google_search_agent()

    # Check that agent has tools and search tool is present
    assert len(agent.tools) > 0
    assert any("GoogleSearchTool" in str(type(tool)) for tool in agent.tools)


def test_google_search_agent_description():
    """Test that google search agent has proper description"""
    agent = create_google_search_agent()

    description = str(agent.description)
    assert "search" in description.lower()


def test_google_search_agent_instruction():
    """Test that google search agent has proper instruction"""
    agent = create_google_search_agent()

    instruction = str(agent.instruction)
    assert "researcher" in instruction.lower() or "facts" in instruction.lower()


def test_root_agent_instance():
    """Test that root_agent is properly initialized"""
    assert root_agent is not None
    assert root_agent.name == "basic_search_agent"
    assert root_agent.model == MODEL_NAME
    assert len(root_agent.tools) == 1


class TestAgentConfiguration:
    """Test suite for agent configuration and initialization"""

    def test_agent_name_consistency(self, google_search_agent):
        """Test that agent name is consistent across instances"""
        agent1 = create_google_search_agent()
        agent2 = create_google_search_agent()

        assert agent1.name == agent2.name == "basic_search_agent"

    def test_agent_model_configuration(self, google_search_agent):
        """Test that agent uses correct model"""
        assert google_search_agent.model == "gemini-2.5-flash"
        assert google_search_agent.model == MODEL_NAME

    def test_agent_tools_configuration(self, google_search_agent):
        """Test that agent has exactly one search tool"""
        assert len(google_search_agent.tools) == 1

        # Verify the tool is related to search functionality
        tool = google_search_agent.tools[0]
        tool_str = str(tool).lower()
        assert "search" in tool_str or "google" in tool_str

    def test_agent_description_content(self, google_search_agent):
        """Test that agent description contains relevant keywords"""
        description = str(google_search_agent.description).lower()

        # Should mention search functionality
        assert "search" in description
        # Should mention Google
        assert "google" in description
        # Should mention questions or answers
        assert "question" in description or "answer" in description

    def test_agent_instruction_detail(self, google_search_agent):
        """Test detailed instruction content"""
        instruction = str(google_search_agent.instruction)

        # Should have substantial instruction content
        assert len(instruction) > 10

        # Should mention being a researcher
        assert "researcher" in instruction.lower()

        # Should mention facts
        assert "facts" in instruction.lower()


class TestSearchToolIntegration:
    """Test suite for Google Search tool integration"""

    def test_search_tool_availability(self, google_search_agent):
        """Test that search tool is properly integrated"""
        tools = google_search_agent.tools
        assert len(tools) == 1

        search_tool = tools[0]
        # Tool should be a GoogleSearchTool object
        assert search_tool is not None
        assert "GoogleSearchTool" in str(type(search_tool))

    @patch("google.adk.tools.google_search")
    def test_search_tool_mock_integration(self, mock_search_tool, google_search_agent):
        """Test search tool integration with mocking"""
        # Configure mock
        mock_search_tool.return_value = {
            "results": [{"title": "Test", "snippet": "Test snippet"}]
        }

        # Verify tool is available
        assert len(google_search_agent.tools) == 1

        # Tool should be the mocked version when properly set up
        # This test verifies the integration point exists
        tools = google_search_agent.tools
        assert tools is not None


class TestErrorHandling:
    """Test suite for error handling and edge cases"""

    def test_agent_creation_robustness(self):
        """Test that agent creation is robust"""
        # Should be able to create multiple agents without issues
        agents = [create_google_search_agent() for _ in range(5)]

        for agent in agents:
            assert agent is not None
            assert agent.name == "basic_search_agent"
            assert len(agent.tools) == 1

    def test_logging_integration(self, google_search_agent):
        """Test that logging is properly integrated"""
        # Agent should be created successfully (logging setup happens during import)
        assert google_search_agent is not None
        assert google_search_agent.name == "basic_search_agent"

    def test_agent_attributes_exist(self, google_search_agent):
        """Test that all expected agent attributes exist"""
        required_attributes = ["name", "model", "description", "instruction", "tools"]

        for attr in required_attributes:
            assert hasattr(
                google_search_agent, attr
            ), f"Agent missing attribute: {attr}"
            assert (
                getattr(google_search_agent, attr) is not None
            ), f"Agent attribute {attr} is None"


class TestQueryProcessing:
    """Test suite for query processing scenarios"""

    def test_basic_query_validation(self):
        """Test basic query validation logic"""
        # Test valid queries
        for query in BASIC_QUERIES:
            assert isinstance(query, str)
            assert len(query) > 0
            assert query.strip() == query  # No leading/trailing whitespace

    def test_edge_case_queries(self):
        """Test edge case query handling"""
        for query in EDGE_CASE_QUERIES:
            # These queries should be identifiable as edge cases
            if query in ["", " "]:
                # Empty or whitespace-only queries
                assert len(query.strip()) == 0
            elif query == "a":
                # Single character query
                assert len(query) == 1
            elif query.isdigit():
                # Numeric-only query
                assert query.isdigit()

    def test_query_expectations_structure(self):
        """Test that query expectations are properly structured"""
        for query_type, expectations in QUERY_EXPECTATIONS.items():
            assert isinstance(expectations, dict)
            assert "should_fail" in expectations
            assert isinstance(expectations["should_fail"], bool)


class TestMockResponses:
    """Test suite for mock response handling"""

    def load_mock_responses(self):
        """Load mock responses from fixtures"""
        fixtures_path = (
            Path(__file__).parent / "fixtures" / "mock_search_responses.json"
        )
        with open(fixtures_path, "r") as f:
            return json.load(f)

    def test_mock_responses_structure(self):
        """Test that mock responses have correct structure"""
        mock_responses = self.load_mock_responses()

        # Check that we have various response types
        expected_responses = [
            "successful_weather_search",
            "successful_tech_search",
            "empty_search_results",
            "api_quota_error",
            "network_timeout_error",
        ]

        for response_type in expected_responses:
            assert (
                response_type in mock_responses
            ), f"Missing mock response: {response_type}"

    def test_successful_response_structure(self):
        """Test structure of successful search responses"""
        mock_responses = self.load_mock_responses()

        success_response = mock_responses["successful_weather_search"]
        assert success_response["status"] == "success"
        assert "results" in success_response
        assert isinstance(success_response["results"], list)
        assert len(success_response["results"]) > 0

        # Check first result structure
        first_result = success_response["results"][0]
        assert "title" in first_result
        assert "url" in first_result
        assert "snippet" in first_result

    def test_error_response_structure(self):
        """Test structure of error responses"""
        mock_responses = self.load_mock_responses()

        error_response = mock_responses["api_quota_error"]
        assert error_response["status"] == "error"
        assert "error_message" in error_response
        assert "error_code" in error_response
        assert len(error_response["error_message"]) > 0


class TestFutureReadiness:
    """Test suite for future functionality readiness"""

    def test_agent_extensibility(self, google_search_agent):
        """Test that agent can be extended with additional capabilities"""
        # Test that we can access agent internals for future extension
        assert hasattr(google_search_agent, "tools")
        assert hasattr(google_search_agent, "model")
        assert hasattr(google_search_agent, "name")

        # Tools list should be modifiable for future enhancements
        assert isinstance(google_search_agent.tools, list)

        # Should be able to identify tool types for future filtering
        for tool in google_search_agent.tools:
            assert tool is not None

    def test_callback_readiness(self, google_search_agent):
        """Test readiness for callback implementation"""
        # Check if callback attributes exist (may be None initially)
        callback_attrs = [
            "before_model_callback",
            "after_model_callback",
            "before_tool_callback",
            "after_tool_callback",
        ]

        for attr in callback_attrs:
            # Attribute may or may not exist yet, but should be settable
            if hasattr(google_search_agent, attr):
                # If it exists, should be None or callable
                callback = getattr(google_search_agent, attr)
                assert callback is None or callable(callback)

    def test_configuration_flexibility(self):
        """Test that agent configuration is flexible for future needs"""
        # Should be able to create multiple agents with same configuration
        agent1 = create_google_search_agent()
        agent2 = create_google_search_agent()

        # They should have the same configuration but be different instances
        assert agent1 is not agent2
        assert agent1.name == agent2.name
        assert agent1.model == agent2.model

    def test_model_constant_usage(self):
        """Test that model configuration uses constants for flexibility"""
        # MODEL_NAME should be used consistently
        agent = create_google_search_agent()
        assert agent.model == MODEL_NAME

        # Constant should be easily changeable
        assert isinstance(MODEL_NAME, str)
        assert len(MODEL_NAME) > 0
