import logging
from google.adk.agents import Agent
from .prompt import instruction as agent_instruction
from home_assistant_client.client import get_state, call_service
from common_logging.logging_utils import setup_logging

# Model configuration
MODEL_NAME = "gemini-2.5-flash"

# Initialize logging for the home assistant agent
setup_logging(service_name="home_assistant_agent")
logger = logging.getLogger(__name__)

logger.info("Initializing Home Assistant Agent")


def create_home_assistant_agent() -> Agent:
    """
    Creates and configures the Home Assistant Agent with smart home integration.

    Returns:
        Agent: Configured Home Assistant Agent instance.
    """
    logger.info(
        f"Creating agent with Home Assistant tools: {get_state}, {call_service}"
    )

    agent = Agent(
        name="home_assistant_agent",
        model=MODEL_NAME,
        description="Helps users monitor and control their smart home devices.",
        instruction=agent_instruction,
        tools=[get_state, call_service],
    )

    logger.debug(f"HA Agent created with {len(agent.tools)} tools")
    return agent
