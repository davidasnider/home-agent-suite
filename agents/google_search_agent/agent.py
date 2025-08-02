import logging
from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool
from common_logging.logging_utils import setup_logging

# Initialize logging for the google search agent
setup_logging(service_name="google_search_agent")
logger = logging.getLogger(__name__)

logger.info("Initializing Google Search Agent")
logger.debug("Agent configuration: name=basic_search_agent, model=gemini-2.0-flash")

root_agent = Agent(
    # A unique name for the agent.
    name="basic_search_agent",
    model="gemini-2.0-flash",
    # A short description of the agent's purpose.
    description="Agent to answer questions using Google Search.",
    # Instructions to set the agent's behavior.
    instruction="You are an expert researcher. You always stick to the facts.",
    # Add google_search tool to perform grounding with Google search.
    tools=[google_search],
)

logger.info(
    "Google Search Agent successfully initialized with %d tool(s)",
    len(root_agent.tools),
)
