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


def _before_model_debug(**kwargs):
    """Debug callback before model is called"""
    logger.info("🚀 BEFORE MODEL CALLBACK")
    logger.info(f"🚀 Kwargs received: {list(kwargs.keys())}")

    callback_context = kwargs.get("callback_context")
    llm_request = kwargs.get("llm_request")

    if callback_context:
        logger.debug(f"🚀 Context type: {type(callback_context)}")
        context_attrs = [
            attr for attr in dir(callback_context) if not attr.startswith("_")
        ]
        logger.debug(f"🚀 Context attributes: {context_attrs}")

        # Log the conversation history
        if hasattr(callback_context, "session") and callback_context.session:
            logger.debug(
                f"🚀 Session has {len(callback_context.session.events)} events"
            )
            for i, event in enumerate(
                callback_context.session.events[:3]
            ):  # Log first 3 events
                if hasattr(event, "content") and event.content:
                    content_preview = (
                        str(event.content)[:100] if event.content else "None"
                    )
                    logger.debug(f"🚀 Event {i}: {content_preview}...")

        # Log available tools
        if hasattr(callback_context, "agent") and callback_context.agent:
            logger.debug(
                f"🚀 Agent has {len(callback_context.agent.tools)} tools available"
            )
            for i, tool in enumerate(callback_context.agent.tools):
                logger.debug(f"🚀 Available tool {i}: {tool}")

    if llm_request:
        logger.info(f"🚀 LLM Request model: {llm_request.model}")
        logger.info(f"🚀 LLM Request has {len(llm_request.contents)} contents")
        if hasattr(llm_request, "config") and llm_request.config:
            tools_count = (
                len(llm_request.config.tools) if llm_request.config.tools else 0
            )
            logger.info(f"🚀 LLM Config tools: {tools_count}")
            if llm_request.config.tools:
                for i, tool in enumerate(llm_request.config.tools):
                    logger.info(f"🚀 Tool {i} in LLM config: {tool}")

        # Log the actual contents being sent to the LLM
        for i, content in enumerate(llm_request.contents):
            logger.info(f"🚀 Content {i}: role={getattr(content, 'role', 'unknown')}")
            if hasattr(content, "parts") and content.parts:
                for j, part in enumerate(content.parts):
                    if hasattr(part, "text") and part.text:
                        text_preview = (
                            part.text[:200] + "..."
                            if len(part.text) > 200
                            else part.text
                        )
                        logger.info(f"🚀 Content {i}, Part {j} text: {text_preview}")

        # Log system instruction
        if (
            hasattr(llm_request.config, "system_instruction")
            and llm_request.config.system_instruction
        ):
            si = llm_request.config.system_instruction
            if hasattr(si, "parts") and si.parts:
                for part in si.parts:
                    if hasattr(part, "text") and part.text:
                        si_preview = (
                            part.text[:300] + "..."
                            if len(part.text) > 300
                            else part.text
                        )
                        logger.info(f"🚀 System Instruction: {si_preview}")


def _after_model_debug(**kwargs):
    """Debug callback after model responds"""
    logger.debug("🎯 AFTER MODEL CALLBACK")
    logger.debug(f"🎯 Kwargs received: {list(kwargs.keys())}")

    response = kwargs.get("response")

    if response:
        logger.debug(f"🎯 Response type: {type(response)}")
        if hasattr(response, "content"):
            content_preview = (
                str(response.content)[:100] if response.content else "None"
            )
            logger.debug(f"🎯 Response content preview: {content_preview}...")


def _before_tool_debug(**kwargs):
    """Debug callback before tool is called"""
    logger.info("🔧 BEFORE TOOL CALLBACK - TOOL IS BEING CALLED!")
    logger.info(f"🔧 Kwargs received: {list(kwargs.keys())}")

    tool = kwargs.get("tool")
    args = kwargs.get("args")

    if tool:
        logger.debug(f"🔧 Tool being called: {tool}")
    if args:
        logger.debug(f"🔧 Tool arguments: {args}")


def _after_tool_debug(**kwargs):
    """Debug callback after tool is called"""
    logger.debug("✅ AFTER TOOL CALLBACK - TOOL COMPLETED!")
    logger.debug(f"✅ Kwargs received: {list(kwargs.keys())}")

    result = kwargs.get("result")
    error = kwargs.get("error")

    if result:
        logger.debug(f"✅ Tool result: {result}")
    if error:
        logger.debug(f"❌ Tool error: {error}")


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
    # DEBUG: Log tool configuration - use INFO level to ensure it shows
    logger.info(f"🔧 Creating agent with weather tool: {get_tmrw_weather_tool}")
    logger.info(
        f"🔧 Tool function name: {getattr(get_tmrw_weather_tool, '__name__', 'unknown')}"
    )
    logger.info(f"🔧 Agent instruction length: {len(agent_instruction)} characters")
    logger.info(f"🔧 Agent instruction preview: {agent_instruction[:200]}...")
    logger.info(
        "🔧 Adding debug callbacks: before_model, after_model, before_tool, after_tool"
    )

    agent = Agent(
        name="day_planner_agent",
        model="gemini-2.5-pro",
        description="Helps users plan their day with weather insights.",
        instruction=agent_instruction,
        tools=[get_tmrw_weather_tool],
        before_model_callback=_before_model_debug,
        after_model_callback=_after_model_debug,
        before_tool_callback=_before_tool_debug,
        after_tool_callback=_after_tool_debug,
    )

    # DEBUG: Log final agent configuration
    logger.debug(f"🔧 Agent created with {len(agent.tools)} tools")
    for i, tool in enumerate(agent.tools):
        logger.debug(f"🔧 Tool {i}: {tool}")

    return agent


# Create the global agent instance
root_agent = create_day_planner_agent()

logger.info(
    "Day Planner Agent successfully initialized with %d tool(s)", len(root_agent.tools)
)
