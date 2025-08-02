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

root_agent = Agent(
    # A unique name for the agent.
    name="day_planner_agent",
    model="gemini-2.5-pro",
    description="Helps users plan their day with weather insights.",
    instruction=agent_instruction,
    # Add weather and search tools for grounding with data.
    tools=[get_tmrw_weather_tool],
)

logger.info(
    "Day Planner Agent successfully initialized with %d tool(s)", len(root_agent.tools)
)
