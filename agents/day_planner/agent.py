from google.adk.agents import Agent
from google.adk.tools import google_search
from .prompt import instruction as agent_instruction


root_agent = Agent(
    # A unique name for the agent.
    name="day_planner_agent",
    model="gemini-2.0-flash",
    description="Helps users plan their day with weather insights.",
    instruction=agent_instruction,
    # Add weather and search tools for grounding with data.
    tools=[google_search],
)
