from google.adk.agents import Agent
from .prompt import instruction as agent_instruction
from tomorrow_io_client.client import get_tmrw_weather_tool


root_agent = Agent(
    # A unique name for the agent.
    name="day_planner_agent",
    model="gemini-2.5-pro",
    description="Helps users plan their day with weather insights.",
    instruction=agent_instruction,
    # Add weather and search tools for grounding with data.
    tools=[get_tmrw_weather_tool],
)
