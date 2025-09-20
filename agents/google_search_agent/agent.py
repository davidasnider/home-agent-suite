"""
Google Search Agent Module

This module defines an intelligent research agent that provides accurate, fact-based
answers using Google Search integration through the Google ADK framework.

The agent specializes in real-time information retrieval, fact verification, and
comprehensive research tasks that require access to current web information.

Key Features:
- Real-time web search capabilities
- Fact-based research and verification
- Current information access beyond training data
- Structured search result analysis

Agent Capabilities:
- Processes complex research queries
- Performs multi-step fact verification
- Synthesizes information from multiple sources
- Provides cited, factual responses

For MCP (Model Context Protocol) integration, this agent:
- Maintains search result traceability
- Provides source attribution for all claims
- Follows structured information retrieval patterns
- Enables composable research workflows
"""

import logging
import re
from google.adk.agents import Agent
from google.adk.tools import google_search
from common_logging.logging_utils import setup_logging

# Model configuration
MODEL_NAME = "gemini-2.5-flash"

# Initialize logging for the google search agent
setup_logging(service_name="google_search_agent")
logger = logging.getLogger(__name__)

logger.info("Initializing Google Search Agent")
logger.debug(f"Agent configuration: name=basic_search_agent, model={MODEL_NAME}")


def create_google_search_agent() -> Agent:
    """
    Creates and configures the Google Search Agent with web search capabilities.

    This function initializes a Google ADK Agent with specialized capabilities
    for web research and fact-based information retrieval. Uses Gemini 2.0 Flash
    for efficient processing of search results and information synthesis.

    Returns:
        Agent: Configured Google Search Agent instance with web search integration

    Agent Configuration:
        - Model: {MODEL_NAME} (optimized for speed and efficiency)
        - Tools: Google Search API integration
        - Capabilities: Web search, fact verification, information synthesis

    Example Usage:
        agent = create_google_search_agent()
        # Agent ready for research and fact-checking queries
    """

    def sanitize_tool_args(**kwargs):
        """A before_tool_callback to sanitize tool arguments."""
        args = kwargs.get("args", {})
        if "query" in args:
            sanitized_query = re.sub(r"[^a-zA-Z0-9\s,.!?-]", "", args["query"])
            args["query"] = sanitized_query

    return Agent(
        name="basic_search_agent",
        model=MODEL_NAME,
        description="Agent to answer questions using Google Search.",
        instruction="You are an expert researcher. You always stick to the facts.",
        tools=[google_search],
        before_tool_callback=sanitize_tool_args,
    )


# Create the global agent instance
root_agent = create_google_search_agent()

logger.info(
    "Google Search Agent successfully initialized with %d tool(s)",
    len(root_agent.tools),
)
