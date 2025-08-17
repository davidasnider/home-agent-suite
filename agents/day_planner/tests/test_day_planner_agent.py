"""
Tests for the Day Planner Agent

These tests verify that the day planner agent is properly created and configured
with the expected model and capabilities.
"""

import os
import sys

# Add the agents directory to the Python path for testing
# This must be done before importing the agent modules
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

from unittest.mock import Mock, patch  # noqa: E402

from day_planner.agent import (  # noqa: E402
    MODEL_NAME,
    create_day_planner_agent,
    _before_model_debug,
    _after_model_debug,
    _before_tool_debug,
    _after_tool_debug,
    root_agent,
)  # noqa: E402


def test_day_planner_agent_creation():
    """Test that day planner agent is created successfully"""
    agent = create_day_planner_agent()

    assert agent is not None
    assert agent.name == "day_planner_agent"
    assert agent.model == MODEL_NAME
    assert agent.model == "gemini-2.5-flash"
    assert len(agent.tools) == 1  # weather tool


def test_day_planner_model_constant():
    """Test that MODEL_NAME constant is correct"""
    assert MODEL_NAME == "gemini-2.5-flash"


def test_day_planner_agent_has_weather_tool():
    """Test that day planner agent has weather tool"""
    agent = create_day_planner_agent()

    # Check that agent has tools and weather tool is present
    assert len(agent.tools) > 0
    tool_names = [str(tool) for tool in agent.tools]
    assert any(
        "weather" in tool_name.lower() or "tmrw" in tool_name.lower()
        for tool_name in tool_names
    )


def test_day_planner_agent_description():
    """Test that day planner agent has proper description"""
    agent = create_day_planner_agent()

    description = str(agent.description)
    assert "weather" in description.lower()
    assert "plan" in description.lower() or "day" in description.lower()


def test_day_planner_agent_has_instruction():
    """Test that day planner agent has instruction configured"""
    agent = create_day_planner_agent()

    assert agent.instruction is not None
    assert len(agent.instruction) > 0
    instruction_lower = agent.instruction.lower()
    assert "weather" in instruction_lower
    assert "get_tmrw_weather_tool" in agent.instruction


def test_day_planner_agent_callbacks_configured():
    """Test that day planner agent has debug callbacks configured"""
    agent = create_day_planner_agent()

    # Check callbacks are set (they should be callable)
    assert callable(agent.before_model_callback)
    assert callable(agent.after_model_callback)
    assert callable(agent.before_tool_callback)
    assert callable(agent.after_tool_callback)


def test_root_agent_instance():
    """Test that root_agent is properly initialized"""
    assert root_agent is not None
    assert root_agent.name == "day_planner_agent"
    assert root_agent.model == MODEL_NAME
    assert len(root_agent.tools) == 1


class TestDebugCallbacks:
    """Test suite for debug callback functions"""

    @patch("day_planner.agent.logger")
    def test_before_model_debug_basic(self, mock_logger):
        """Test before_model_debug with basic kwargs"""
        kwargs = {}
        _before_model_debug(**kwargs)

        mock_logger.info.assert_called()
        assert any(
            "BEFORE MODEL CALLBACK" in str(call)
            for call in mock_logger.info.call_args_list
        )

    @patch("day_planner.agent.logger")
    def test_before_model_debug_with_callback_context(self, mock_logger):
        """Test before_model_debug with callback_context"""
        mock_context = Mock()
        mock_context.session = Mock()
        mock_context.session.events = [
            Mock(content="test content"),
            Mock(content="test content 2"),
        ]
        mock_context.agent = Mock()
        mock_context.agent.tools = [Mock(), Mock()]

        kwargs = {"callback_context": mock_context}
        _before_model_debug(**kwargs)

        mock_logger.info.assert_called()
        mock_logger.debug.assert_called()

    @patch("day_planner.agent.logger")
    def test_before_model_debug_with_llm_request(self, mock_logger):
        """Test before_model_debug with llm_request"""
        mock_llm_request = Mock()
        mock_llm_request.model = "test-model"
        mock_llm_request.contents = [Mock(), Mock()]
        mock_llm_request.config = Mock()
        mock_llm_request.config.tools = [Mock(), Mock()]
        mock_llm_request.config.system_instruction = Mock()
        mock_llm_request.config.system_instruction.parts = [Mock()]
        mock_llm_request.config.system_instruction.parts[0].text = "test instruction"

        # Mock content with parts
        for i, content in enumerate(mock_llm_request.contents):
            content.role = f"role_{i}"
            content.parts = [Mock()]
            content.parts[0].text = f"test content {i}"

        kwargs = {"llm_request": mock_llm_request}
        _before_model_debug(**kwargs)

        mock_logger.info.assert_called()

    @patch("day_planner.agent.logger")
    def test_after_model_debug(self, mock_logger):
        """Test after_model_debug callback"""
        mock_response = Mock()
        mock_response.content = "test response content"

        kwargs = {"response": mock_response}
        _after_model_debug(**kwargs)

        mock_logger.debug.assert_called()
        assert any(
            "AFTER MODEL CALLBACK" in str(call)
            for call in mock_logger.debug.call_args_list
        )

    @patch("day_planner.agent.logger")
    def test_before_tool_debug(self, mock_logger):
        """Test before_tool_debug callback"""
        mock_tool = Mock()
        mock_args = {"location": "test location"}

        kwargs = {"tool": mock_tool, "args": mock_args}
        _before_tool_debug(**kwargs)

        mock_logger.info.assert_called()
        assert any(
            "BEFORE TOOL CALLBACK" in str(call)
            for call in mock_logger.info.call_args_list
        )

    @patch("day_planner.agent.logger")
    def test_after_tool_debug_with_result(self, mock_logger):
        """Test after_tool_debug callback with result"""
        mock_result = {"status": "success", "forecast": "sunny"}

        kwargs = {"result": mock_result}
        _after_tool_debug(**kwargs)

        mock_logger.debug.assert_called()
        assert any(
            "AFTER TOOL CALLBACK" in str(call)
            for call in mock_logger.debug.call_args_list
        )

    @patch("day_planner.agent.logger")
    def test_after_tool_debug_with_error(self, mock_logger):
        """Test after_tool_debug callback with error"""
        mock_error = Exception("test error")

        kwargs = {"error": mock_error}
        _after_tool_debug(**kwargs)

        mock_logger.debug.assert_called()
        assert any(
            "AFTER TOOL CALLBACK" in str(call)
            for call in mock_logger.debug.call_args_list
        )


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    @patch("day_planner.agent.logger")
    def test_before_model_debug_empty_session_events(self, mock_logger):
        """Test before_model_debug with empty session events"""
        mock_context = Mock()
        mock_context.session = Mock()
        mock_context.session.events = []
        mock_context.agent = Mock()
        mock_context.agent.tools = []

        kwargs = {"callback_context": mock_context}
        _before_model_debug(**kwargs)

        mock_logger.debug.assert_called()

    @patch("day_planner.agent.logger")
    def test_before_model_debug_no_system_instruction(self, mock_logger):
        """Test before_model_debug with llm_request without system instruction"""
        mock_llm_request = Mock()
        mock_llm_request.model = "test-model"
        mock_llm_request.contents = []
        mock_llm_request.config = Mock()
        mock_llm_request.config.tools = None
        mock_llm_request.config.system_instruction = None

        kwargs = {"llm_request": mock_llm_request}
        _before_model_debug(**kwargs)

        mock_logger.info.assert_called()

    @patch("day_planner.agent.logger")
    def test_before_model_debug_long_content(self, mock_logger):
        """Test before_model_debug with long content that gets truncated"""
        mock_llm_request = Mock()
        mock_llm_request.model = "test-model"
        mock_llm_request.contents = [Mock()]
        mock_llm_request.config = Mock()
        mock_llm_request.config.tools = []
        mock_llm_request.config.system_instruction = None  # Avoid iteration error

        # Create long content that should be truncated
        long_text = "a" * 300
        mock_llm_request.contents[0].role = "user"
        mock_llm_request.contents[0].parts = [Mock()]
        mock_llm_request.contents[0].parts[0].text = long_text

        kwargs = {"llm_request": mock_llm_request}
        _before_model_debug(**kwargs)

        mock_logger.info.assert_called()

        # Check that truncation occurred
        logged_calls = [str(call) for call in mock_logger.info.call_args_list]
        content_call = next(
            (call for call in logged_calls if "Content 0, Part 0 text:" in call), None
        )
        assert content_call is not None
        assert "..." in content_call

    @patch("day_planner.agent.logger")
    def test_after_model_debug_no_response(self, mock_logger):
        """Test after_model_debug with no response"""
        kwargs = {}
        _after_model_debug(**kwargs)

        mock_logger.debug.assert_called()

    @patch("day_planner.agent.logger")
    def test_callback_context_without_attributes(self, mock_logger):
        """Test before_model_debug with callback_context missing attributes"""
        mock_context = Mock()
        # Remove the session and agent attributes
        del mock_context.session
        del mock_context.agent

        kwargs = {"callback_context": mock_context}
        _before_model_debug(**kwargs)

        mock_logger.debug.assert_called()


@patch("day_planner.agent.logger")
def test_create_day_planner_agent_logging(mock_logger):
    """Test that create_day_planner_agent logs configuration details"""
    create_day_planner_agent()

    # Verify logging calls were made
    mock_logger.info.assert_called()
    mock_logger.debug.assert_called()

    # Check specific log messages
    info_calls = [str(call) for call in mock_logger.info.call_args_list]
    debug_calls = [str(call) for call in mock_logger.debug.call_args_list]

    assert any("Creating agent with weather tool" in call for call in info_calls)
    assert any("Tool function name" in call for call in info_calls)
    assert any("Agent instruction length" in call for call in info_calls)
    assert any("Adding debug callbacks" in call for call in info_calls)
    assert any("Agent created with" in call for call in debug_calls)


def test_agent_configuration_constants():
    """Test agent configuration constants"""
    assert MODEL_NAME == "gemini-2.5-flash"

    agent = create_day_planner_agent()
    assert agent.name == "day_planner_agent"
    assert agent.model == MODEL_NAME
    assert len(agent.tools) == 1
