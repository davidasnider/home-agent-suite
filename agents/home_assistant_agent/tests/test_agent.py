from google.adk.agents import Agent
from agents.home_assistant_agent.agent import create_home_assistant_agent


def test_create_home_assistant_agent():
    agent = create_home_assistant_agent()
    assert isinstance(agent, Agent)
    assert agent.name == "home_assistant_agent"
    assert len(agent.tools) == 2
    tool_names = [
        getattr(tool, "name", getattr(tool, "__name__", None)) for tool in agent.tools
    ]
    assert "get_state" in tool_names
    assert "call_service" in tool_names


def test_agent_instruction():
    agent = create_home_assistant_agent()
    assert "Home Assistant Agent" in agent.instruction
    assert "get_state" in agent.instruction
    assert "call_service" in agent.instruction
