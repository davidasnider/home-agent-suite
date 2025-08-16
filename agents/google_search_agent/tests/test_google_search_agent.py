"""
Tests for the Google Search Agent

These tests verify that the google search agent is properly created and configured
with the expected model and capabilities.
"""

import os
import sys

# Add the agents directory to the Python path for testing
# This must be done before importing the agent modules
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

from google_search_agent.agent import (  # noqa: E402
    MODEL_NAME,
    create_google_search_agent,
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
    tool_names = [str(tool) for tool in agent.tools]
    assert any(
        "search" in tool_name.lower() or "google" in tool_name.lower()
        for tool_name in tool_names
    )


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
