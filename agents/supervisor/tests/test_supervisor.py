"""
Tests for the Supervisor Agent

These tests verify that the supervisor agent is properly created and configured
with the expected tools and capabilities.
"""

from supervisor.agent import create_supervisor_agent, MODEL_NAME


def test_supervisor_agent_creation():
    """Test that supervisor agent is created successfully"""
    agent = create_supervisor_agent()

    assert agent is not None
    assert agent.name == "supervisor_agent"
    assert agent.model == MODEL_NAME
    assert agent.model == "gemini-2.5-pro"
    assert len(agent.tools) == 2  # weather tool + google search


def test_supervisor_agent_has_weather_tool():
    """Test that supervisor agent has weather tool"""
    agent = create_supervisor_agent()

    # Check for day_planner_agent within AgentTool objects
    assert any(
        hasattr(tool, "agent") and "day_planner" in tool.agent.name.lower()
        for tool in agent.tools
    )


def test_supervisor_agent_has_search_tool():
    """Test that supervisor agent has search tool"""
    agent = create_supervisor_agent()

    # Check for search_agent within AgentTool objects
    assert any(
        hasattr(tool, "agent") and "search" in tool.agent.name.lower()
        for tool in agent.tools
    )


def test_supervisor_agent_instruction():
    """Test that supervisor agent has proper instruction"""
    agent = create_supervisor_agent()

    instruction = agent.instruction
    assert "supervisor" in instruction.lower() or "delegate" in instruction.lower()
    assert "weather" in instruction.lower()
    assert "search" in instruction.lower()


def test_supervisor_model_constant():
    """Test that MODEL_NAME constant is correct"""
    assert MODEL_NAME == "gemini-2.5-pro"
