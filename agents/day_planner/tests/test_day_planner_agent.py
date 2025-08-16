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

from day_planner.agent import MODEL_NAME, create_day_planner_agent  # noqa: E402


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
