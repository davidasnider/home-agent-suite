import streamlit as st
import time
import logging
from datetime import datetime
from common_logging.logging_utils import setup_logging

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Import supervisor agent
try:
    from supervisor.agent import create_supervisor_agent

    SUPERVISOR_AVAILABLE = True
except Exception as e:
    SUPERVISOR_AVAILABLE = False
    supervisor_error = str(e)

# Initialize logging
setup_logging(service_name="streamlit_chatbot_backend")
logger = logging.getLogger("chatbot_backend")
logger.setLevel(logging.DEBUG)


class ChatbotManager:
    """Manages chatbot agents and conversation state"""

    def __init__(self):
        self.agents = {}
        self.runners = {}  # Store runners to maintain session state

        # Create a shared session service for all runners to ensure session persistence
        from google.adk.sessions.in_memory_session_service import InMemorySessionService

        self.shared_session_service = InMemorySessionService()
        logger.debug(
            f"🗃️ Created shared session service: {id(self.shared_session_service)}"
        )

        # Initialize supervisor agent only
        if SUPERVISOR_AVAILABLE:
            try:
                self.agents["supervisor"] = create_supervisor_agent()
                logger.info("Supervisor agent initialized")
            except Exception as e:
                logger.error(f"Failed to initialize supervisor agent: {e}")
                logger.warning("Supervisor failed, adding demo agent")
                self.agents["demo"] = self._create_demo_agent()
        else:
            logger.error(f"Supervisor agent not available: {supervisor_error}")
            self.agents["demo"] = self._create_demo_agent()
            logger.info("Using demo agent as fallback")

        logger.info("Chatbot manager initialized with %d agents", len(self.agents))

    def _create_demo_agent(self):
        """Create a demo agent for when real agents aren't available"""

        class DemoAgent:
            def __init__(self):
                self.name = "Demo Agent"

            def chat(self, message):
                return (
                    f"🤖 Demo Agent Response: I received your message "
                    f"'{message}'. This is a demonstration of the chat "
                    "interface. Real agent integration requires proper API "
                    "keys and configuration."
                )

        return DemoAgent()

    def get_agent_response(self, agent_name: str, message: str) -> str:
        """Get response from specified agent"""
        try:
            if agent_name not in self.agents:
                available = ", ".join(self.agents.keys())
                return f"❌ Agent '{agent_name}' not found. Available: {available}"

            agent = self.agents[agent_name]

            # Handle demo agent directly without using the ADK InMemoryRunner
            if agent_name == "demo":
                try:
                    logger.info("Using DemoAgent for demo mode")
                    return agent.chat(message)
                except Exception as agent_error:
                    error_str = str(agent_error)
                    logger.error(
                        "Demo agent call failed for %s: %s",
                        agent_name,
                        error_str,
                    )
                    ellipsis = "..." if len(message) > 50 else ""
                    agent_title = agent_name.replace("_", " ").title()
                    return (
                        f"🤖 {agent_title} Agent (Demo): I received your "
                        f"message '{message[:50]}{ellipsis}'.\n\n⚠️ Demo "
                        f"Agent Error: {error_str}"
                    )

            # Call the actual Google ADK agent
            try:
                logger.info(f"Initializing agent: {agent_name}")
                from google.adk.runners import InMemoryRunner
                from google.genai import types
                import asyncio

                if agent_name not in self.runners:
                    try:
                        # Use agent.name for app_name consistency with ADK
                        logger.info(
                            "Creating InMemoryRunner for %s " "using agent.name: %s",
                            agent_name,
                            agent.name,
                        )
                        self.runners[agent_name] = InMemoryRunner(
                            agent=agent,
                            app_name=agent.name,
                            session_service=self.shared_session_service,
                        )
                        logger.info(
                            "Created InMemoryRunner for %s with shared session service",
                            agent_name,
                        )
                    except TypeError:
                        # Fallback if constructor doesn't accept session_service
                        self.runners[agent_name] = InMemoryRunner(
                            agent=agent, app_name=agent.name
                        )
                        self.runners[agent_name].session_service = (
                            self.shared_session_service
                        )
                        logger.info(
                            "Assigned shared session service to InMemoryRunner for %s",
                            agent_name,
                        )
                    except Exception as runner_error:
                        logger.error(f"Failed to create Runner: {runner_error}")
                        raise Exception(
                            f"Failed to create ADK Runner for agent {agent_name}"
                        )

                runner = self.runners[agent_name]

                # Verify identity for debugging
                logger.debug(
                    "Manager shared_session_service ID: %s",
                    id(self.shared_session_service),
                )
                logger.debug(
                    "Runner session_service ID: %s", id(runner.session_service)
                )

                logger.info("Processing message for %s", agent.name)

                try:
                    user_content = types.Content(
                        parts=[types.Part.from_text(text=message)], role="user"
                    )
                    user_id = "streamlit_user"
                    try:
                        session_id = st.session_state.conversation_id
                    except AttributeError:
                        session_id = "test_session"

                    async def run_agent():
                        # Robust session init: try app_name and agent.name
                        app_names_to_try = {
                            runner.app_name,
                            agent.name,
                            agent_name,
                        }
                        for name in app_names_to_try:
                            if not name:
                                continue
                            try:
                                await runner.session_service.create_session(
                                    app_name=name,
                                    user_id=user_id,
                                    session_id=session_id,
                                )
                                logger.info(
                                    "✨ Created new session for app='%s', "
                                    "user='%s', session='%s'",
                                    name,
                                    user_id,
                                    session_id,
                                )
                            except Exception:
                                # Session likely already exists, which is fine
                                logger.debug(
                                    "ℹ️ Session for app='%s' already exists "
                                    "or could not be created",
                                    name,
                                )

                        responses = []
                        from google.adk.agents.run_config import (
                            RunConfig,
                            StreamingMode,
                        )

                        logger.info(
                            "🚀 Calling runner.run_async: session=%s, user=%s",
                            session_id,
                            user_id,
                        )
                        async for event in runner.run_async(
                            user_id=user_id,
                            session_id=session_id,
                            new_message=user_content,
                            state_delta=None,
                            run_config=RunConfig(streaming_mode=StreamingMode.NONE),
                        ):
                            await self._process_event_async(event, responses)
                        return responses

                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    responses = loop.run_until_complete(run_agent())
                    response = (
                        "\n".join(responses) if responses else "No response from agent"
                    )
                except Exception as e:
                    logger.error(f"Error in runner async call: {e}")
                    raise
                return str(response)

            except Exception as agent_error:
                error_str = str(agent_error)
                logger.error(
                    "Agent call failed for %s: %s",
                    agent_name,
                    error_str,
                )
                ellipsis = "..." if len(message) > 50 else ""
                agent_title = agent_name.replace("_", " ").title()
                return (
                    f"🤖 {agent_title} Agent: I received your message "
                    f"'{message[:50]}{ellipsis}'.\n\n⚠️ Agent Error: "
                    f"{error_str}\n\nThis indicates the agent integration "
                    "needs to be updated for the correct Google ADK API."
                )
        except Exception as e:
            error_str = str(e)
            logger.error("Error getting response from %s: %s", agent_name, error_str)
            msg = "❌ Sorry, I encountered an error while processing: %s"
            return msg % error_str

    async def _process_event_async(self, event, responses):
        """Process a single event from the agent runner"""
        try:
            event_text = self._extract_text_from_event(event)
            if event_text:
                responses.append(event_text)
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            responses.append(f"Error processing response: {str(e)}")

    def _extract_text_from_event(self, event):
        """Extract text content from various ADK Event structures"""
        if hasattr(event, "actions") and event.actions:
            for action in event.actions:
                if hasattr(action, "text") and action.text:
                    return action.text
                elif hasattr(action, "content") and action.content:
                    if hasattr(action.content, "parts"):
                        for part in action.content.parts:
                            if hasattr(part, "text") and part.text:
                                return part.text
                    else:
                        return str(action.content)
        if hasattr(event, "content") and event.content:
            if hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        return part.text
            elif hasattr(event.content, "text"):
                return event.content.text
            else:
                return str(event.content)
        elif hasattr(event, "text") and event.text:
            return event.text
        return None

    def get_primary_agent(self) -> str:
        """Get the primary agent (supervisor or demo fallback)"""
        return "supervisor" if "supervisor" in self.agents else "demo"


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hello! I'm your intelligent Home Agent Suite assistant. "
                    "I can help you with:\n\n"
                    "🌤️ **Weather & Planning** - Daily forecasts, "
                    "activity suggestions, optimal timing\n"
                    "🔍 **Research & Information** - Facts, current events, "
                    "explanations\n\n"
                    "Just ask me anything and I'll automatically choose "
                    "the best approach to help you!"
                ),
                "timestamp": datetime.now().isoformat(),
                "agent": "supervisor",
            }
        ]

    if "chatbot_manager" not in st.session_state:
        st.session_state.chatbot_manager = ChatbotManager()
        logger.debug("Created new ChatbotManager in session state")

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = f"chat_{int(time.time())}"

    if "last_request_time" not in st.session_state:
        st.session_state.last_request_time = 0
