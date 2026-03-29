"""
Supervisor Agent Module

This module defines a hierarchical supervisor agent that intelligently delegates
tasks to specialized sub-agents using Google ADK's LLM-based tool selection.

The supervisor agent uses a carefully crafted prompt to guide the LLM in choosing
the appropriate specialized agent based on query content and user intent.

Key Features:
- Intelligent delegation through LLM reasoning
- Integration with day planner and search agents
- Unified conversation interface
- Context preservation across agent interactions
"""

import logging
from google.adk.agents import Agent
from google.adk.tools import agent_tool

# Import dependencies using sys.path until agents are proper packages
import sys
import os

# Add agents directory to sys.path for imports
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

try:
    from day_planner.agent import create_day_planner_agent  # noqa: E402
    from google_search_agent.agent import create_google_search_agent  # noqa: E402
    from home_assistant_agent.agent import create_home_assistant_agent  # noqa: E402
    from common_logging.logging_utils import setup_logging  # noqa: E402
except ImportError as e:
    raise ImportError(
        f"Failed to import required dependencies: {e}. " f"Searched in: {agents_dir}"
    )

# Model configuration
MODEL_NAME = "gemini-2.5-flash"

# Initialize logging for the supervisor agent
setup_logging(service_name="supervisor_agent")
logger = logging.getLogger(__name__)

logger.info("Initializing Supervisor Agent")


def create_supervisor_agent() -> Agent:
    """
    Creates and configures the Supervisor Agent with delegation capabilities.

    This agent acts as an intelligent router that analyzes user queries and
    delegates them to the most appropriate specialized agent. It uses the LLM's
    reasoning capabilities to make delegation decisions through a detailed prompt.

    Returns:
        Agent: Configured Supervisor Agent with access to all specialized tools

    Agent Configuration:
        - Model: {MODEL_NAME} (for sophisticated reasoning and delegation)
        - Tools: All tools from specialized agents (weather, search, home assistant)
        - Capabilities: Query analysis, intelligent routing, unified responses
    """

    # Comprehensive instruction for intelligent delegation
    supervisor_instruction = (
        "You are a Supervisor Agent that helps users by intelligently "
        "choosing the right approach for their queries.\n\n"
        "You have access to multiple specialized capabilities through these "
        "tools:\n\n"
        "WEATHER & ACTIVITY PLANNING (day_planner_agent):\n"
        "- Use for weather forecasts, daily planning, activity suggestions\n"
        "- Use when users ask about outdoor activities, weather conditions, "
        "or time-based planning\n\n"
        "SMART HOME CONTROL (home_assistant_agent):\n"
        "- Use for home automation, device status, and device control\n"
        "- Use when users ask to turn things on/off or query status (locks, lights)\n"
        "- Examples: 'Turn off the living room lights', 'Is the front door "
        "locked?', 'Check the thermostat status'\n\n"
        "GENERAL INFORMATION & RESEARCH (google_search_agent):\n"
        "- Use for factual information, current events, definitions, "
        "explanations\n"
        "- Use when users need information beyond weather and home automation\n"
        "- Examples: 'What is quantum computing?', 'Latest news about AI'\n\n"
        "DECISION MAKING GUIDELINES:\n\n"
        "1. WEATHER & PLANNING:\n"
        "   - Route directly to day_planner_agent for ANY query about weather, "
        "hiking, outdoor activities, or daily planning.\n"
        "   - IMPORTANT: If you just asked for the user's location and they provide "
        "it (e.g., 'Seattle' or 'Marion montana'), route that location directly "
        "to day_planner_agent so it can complete the planning task.\n"
        "   - Do NOT use google_search_agent for simple location lookups related to "
        "weather or planning; day_planner_agent handles this internally.\n\n"
        "2. HOME AUTOMATION:\n"
        "   - Route to home_assistant_agent for all device-related queries.\n\n"
        "3. GENERAL INFORMATION:\n"
        "   - Use google_search_agent for factual questions, news, and "
        "general research that is UNRELATED to weather or home control.\n\n"
        "Always maintain conversation context. If a user provides information "
        "requested by a sub-agent, ensure that same sub-agent receives it.\n\n"
        "Always provide helpful, accurate responses and explain your reasoning "
        "when choosing between different approaches. Be conversational and "
        "friendly while maintaining accuracy."
    )

    logger.info("Creating supervisor agent with AgentTool wrappers")

    day_planner_agent = create_day_planner_agent()
    search_agent = create_google_search_agent()
    ha_agent = create_home_assistant_agent()

    # Wrap sub-agents as tools using AgentTool
    day_planner_tool = agent_tool.AgentTool(agent=day_planner_agent)
    search_tool = agent_tool.AgentTool(agent=search_agent)
    ha_tool = agent_tool.AgentTool(agent=ha_agent)

    agent = Agent(
        name="supervisor_agent",
        model=MODEL_NAME,
        description=(
            "Intelligent supervisor agent that delegates queries to "
            "specialized capabilities"
        ),
        instruction=supervisor_instruction,
        tools=[day_planner_tool, search_tool, ha_tool],
    )

    logger.info(f"Supervisor agent created with {len(agent.tools)} tools")
    for i, tool in enumerate(agent.tools):
        logger.info(f"Tool {i}: {tool.name}")

    return agent


# Create the global supervisor agent instance
root_agent = create_supervisor_agent()

logger.info(
    "Supervisor Agent successfully initialized with %d tool(s)", len(root_agent.tools)
)
