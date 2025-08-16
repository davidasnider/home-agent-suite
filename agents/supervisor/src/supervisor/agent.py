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
    from day_planner.agent import create_day_planner_agent
    from google_search_agent.agent import create_google_search_agent
    from common_logging.logging_utils import setup_logging
except ImportError as e:
    raise ImportError(
        f"Failed to import required dependencies: {e}. " f"Searched in: {agents_dir}"
    )

# Model configuration
MODEL_NAME = "gemini-2.5-pro"

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
        - Tools: All tools from specialized agents (weather, search)
        - Capabilities: Query analysis, intelligent routing, unified responses
    """

    # Comprehensive instruction for intelligent delegation
    supervisor_instruction = (
        "You are a Supervisor Agent that helps users by intelligently "
        "choosing the right approach for their queries.\n\n"
        "You have access to multiple specialized capabilities through these "
        "tools:\n\n"
        "WEATHER & ACTIVITY PLANNING (get_tmrw_weather_tool):\n"
        "- Use for weather forecasts, daily planning, activity suggestions\n"
        "- Use when users ask about outdoor activities, weather conditions, "
        "or time-based planning\n"
        "- Use for location-based recommendations and weather-dependent "
        "decisions\n"
        "- Examples: 'What's the weather?', 'Should I go hiking today?', "
        "'Plan my day in Seattle'\n\n"
        "GENERAL INFORMATION & RESEARCH (google_search):\n"
        "- Use for factual information, current events, definitions, "
        "explanations\n"
        "- Use when users need information beyond weather and planning\n"
        "- Use for 'what is', 'who is', 'how does', research questions\n"
        "- Examples: 'What is quantum computing?', 'Who won the Super Bowl?', "
        "'How does photosynthesis work?'\n\n"
        "CRITICAL RULE: For weather queries mentioning a specific city, "
        "you MUST follow this exact two-step process:\n\n"
        "STEP 1: Call google_search_agent to find '[City Name] coordinates "
        "latitude longitude'\n"
        "STEP 2: Call day_planner_agent with the coordinates in the format "
        "'latitude,longitude' as a single location string\n\n"
        "NEVER call day_planner_agent directly with city names. Always get "
        "coordinates first.\n\n"
        "Examples requiring this workflow:\n"
        "- 'Weather in Seattle' → google_search_agent('Seattle coordinates') "
        "→ day_planner_agent('47.6062,-122.3321')\n"
        "- 'Denver weather' → google_search_agent('Denver Colorado coordinates') "
        "→ day_planner_agent('39.7392,-104.9903')\n"
        "- 'What should I do in Austin?' → google_search_agent('Austin Texas "
        "coordinates') → day_planner_agent('30.2672,-97.7431')\n\n"
        "DECISION MAKING GUIDELINES:\n\n"
        "1. WEATHER QUERIES WITH CITY NAMES:\n"
        "   ✅ CORRECT: google_search_agent → day_planner_agent\n"
        "   ❌ WRONG: day_planner_agent directly with city name\n\n"
        "2. GENERAL INFORMATION queries use google_search_agent only:\n"
        "   - Factual questions ('What is the capital of France?')\n"
        "   - Current events ('Latest news about AI')\n"
        "   - Definitions and explanations ('How does blockchain work?')\n\n"
        "3. WEATHER queries WITHOUT specific cities:\n"
        "   - 'What's the weather?' → Ask user for location first\n\n"
        "Always provide helpful, accurate responses and explain your reasoning "
        "when choosing between different approaches. Be conversational and "
        "friendly while maintaining accuracy."
    )

    logger.info("Creating supervisor agent with AgentTool wrappers")
    day_planner_agent = create_day_planner_agent()
    search_agent = create_google_search_agent()

    # Wrap sub-agents as tools using AgentTool
    day_planner_tool = agent_tool.AgentTool(agent=day_planner_agent)
    search_tool = agent_tool.AgentTool(agent=search_agent)

    agent = Agent(
        name="supervisor_agent",
        model=MODEL_NAME,
        description=(
            "Intelligent supervisor agent that delegates queries to "
            "specialized capabilities"
        ),
        instruction=supervisor_instruction,
        tools=[day_planner_tool, search_tool],
    )

    logger.info(f"Supervisor agent created with {len(agent.tools)} tools")
    for i, tool in enumerate(agent.tools):
        logger.info(f"Tool {i}: {tool}")

    return agent


# Create the global supervisor agent instance
root_agent = create_supervisor_agent()

logger.info(
    "Supervisor Agent successfully initialized with %d tool(s)", len(root_agent.tools)
)
