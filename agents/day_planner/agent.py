"""
Day Planner Agent Module

This module defines an intelligent day planning agent that provides personalized
activity recommendations based on real-time weather data from Tomorrow.io API.

The agent uses Google ADK (Agent Development Kit) to process natural language
queries and provide contextual suggestions for daily activities, optimizing for
weather conditions.

Key Features:
- Weather-aware activity recommendations
- Location-based planning suggestions
- Time-specific outdoor activity windows
- Indoor alternatives for poor weather

Agent Capabilities:
- Processes location queries (city names, coordinates)
- Analyzes hourly weather forecasts
- Suggests optimal time windows for activities
- Provides backup indoor activity recommendations

For MCP (Model Context Protocol) integration, this agent:
- Follows structured tool calling patterns
- Provides deterministic, weather-grounded responses
- Maintains conversation context for follow-up queries
"""

import logging
from google.adk.agents import Agent
from .prompt import instruction as agent_instruction
from tomorrow_io_client.client import get_tmrw_weather_tool
from common_logging.logging_utils import setup_logging

# Initialize logging for the day planner agent
setup_logging(service_name="day_planner_agent")
logger = logging.getLogger(__name__)

logger.info("Initializing Day Planner Agent")
logger.debug("Agent configuration: name=day_planner_agent, model=gemini-2.5-pro")


def create_day_planner_agent() -> Agent:
    """
    Creates and configures the Day Planner Agent with weather integration.

    This function initializes a Google ADK Agent with specialized capabilities
    for weather-based day planning. The agent uses the Gemini 2.5 Pro model
    for sophisticated reasoning about weather patterns and activity recommendations.

    Returns:
        Agent: Configured Day Planner Agent instance with weather tool integration

    Agent Configuration:
        - Model: gemini-2.5-pro (for advanced reasoning)
        - Tools: Tomorrow.io weather API integration
        - Capabilities: Location parsing, weather analysis, activity suggestions

    Example Usage:
        agent = create_day_planner_agent()
        # Agent ready for weather-based planning queries
    """
    return Agent(
        name="day_planner_agent",
        model="gemini-2.5-pro",
        description="Helps users plan their day with weather insights.",
        instruction=agent_instruction,
        tools=[get_tmrw_weather_tool],
    )


# Create the global agent instance
root_agent = create_day_planner_agent()

logger.info(
    "Day Planner Agent successfully initialized with %d tool(s)", len(root_agent.tools)
)
