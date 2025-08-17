"""
Streamlit Chatbot Application

A modern, responsive chat interface that integrates with the home-agent-suite's
existing Google ADK agents for intelligent home automation and planning assistance.

Features:
- Clean, modern design with Streamlit's native chat components
- Session state management for conversation persistence
- Integration with day planner and Google search agents
- Mobile-responsive layout with sidebar controls
- Message avatars and typing indicators
- Export and clear chat history functionality
- Custom CSS styling for enhanced user experience
"""

import streamlit as st
import time
import json
import logging
from datetime import datetime

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

from common_logging.logging_utils import setup_logging

# Initialize logging
setup_logging(service_name="streamlit_chatbot")
logger = logging.getLogger(__name__)  # TODO don't use __name__ give it a better name
logger.setLevel(logging.DEBUG)  # Enable debug logging for detailed agent info

# Page configuration
st.set_page_config(
    page_title="Home Agent Suite Chat",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/davidasnider/home-agent-suite",
        "Report a bug": "https://github.com/davidasnider/home-agent-suite/issues",
        "About": (
            "Home Agent Suite - Intelligent home automation and planning" " assistant"
        ),
    },
)


# Custom CSS for enhanced styling
def load_custom_css():
    """Load custom CSS for enhanced styling"""
    st.markdown(
        """
    <style>
    /* Main chat container styling */
    .stChatMessage {
        background-color: var(--background-color);
        border-radius: 15px;
        margin: 10px 0;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    /* User message styling */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20px;
    }

    /* Assistant message styling */
    .stChatMessage[data-testid="assistant-message"] {
        background: var(--secondary-background-color);
        border-left: 4px solid #00d4aa;
        margin-right: 20px;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* Chat input styling */
    .stChatInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #00d4aa;
        padding: 12px 20px;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 20px;
        border: none;
        background: linear-gradient(45deg, #00d4aa 0%, #00b894 100%);
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,212,170,0.3);
    }

    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 10px 20px;
        background: var(--secondary-background-color);
        border-radius: 15px;
        margin: 10px 0;
    }

    .typing-dots {
        display: flex;
        gap: 4px;
    }

    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00d4aa;
        animation: typing 1.4s infinite;
    }

    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
        30% { transform: translateY(-10px); opacity: 1; }
    }

    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .stChatMessage {
            margin: 5px 0;
            padding: 12px;
        }

        .stChatMessage[data-testid="user-message"] {
            margin-left: 10px;
        }

        .stChatMessage[data-testid="assistant-message"] {
            margin-right: 10px;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


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
                logger.info("Supervisor agent initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize supervisor agent: {e}")
                # Fallback to demo agent if supervisor fails
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
                return (
                    f"❌ Agent '{agent_name}' not found. Available agents: "
                    f"{', '.join(self.agents.keys())}"
                )

            agent = self.agents[agent_name]

            # Call the actual Google ADK agent
            try:
                # Log agent initialization for troubleshooting
                logger.info(f"Initializing agent: {agent_name}")

                # Use InMemoryRunner with proper run_async call like ADK web does
                from google.adk.runners import InMemoryRunner
                from google.genai import types
                import asyncio

                # Get or create a persistent runner for this agent with shared
                # session service
                if agent_name not in self.runners:
                    try:
                        # Create runner - InMemoryRunner manages its own session service
                        self.runners[agent_name] = InMemoryRunner(
                            agent=agent, app_name=agent_name
                        )

                        # Override the session service to use our shared one for
                        # session persistence
                        self.runners[agent_name].session_service = (
                            self.shared_session_service
                        )
                        logger.info(f"Created InMemoryRunner for {agent_name}")
                    except Exception as runner_error:
                        logger.error(f"Failed to create Runner: {runner_error}")
                        raise Exception(
                            f"Failed to create ADK Runner for agent {agent_name}"
                        )

                runner = self.runners[agent_name]

                logger.info(f"Processing message for {agent.name}")

                try:
                    # Create the content for the user message exactly like ADK web does
                    user_content = types.Content(
                        parts=[types.Part.from_text(text=message)], role="user"
                    )

                    # Use consistent session ID from Streamlit session state
                    # (with fallback for testing)
                    user_id = "streamlit_user"
                    try:
                        session_id = st.session_state.conversation_id
                        logger.debug(f"Using session: {session_id}")
                    except AttributeError:
                        # Fallback for non-Streamlit contexts (testing)
                        session_id = "test_session"
                        logger.debug(f"Using fallback session: {session_id}")

                    async def run_agent():
                        """Async wrapper for runner call - exactly like ADK web"""
                        # Check if session exists first, create only if needed
                        existing_session = None
                        try:
                            existing_session = await runner.session_service.get_session(
                                app_name=agent_name,
                                user_id=user_id,
                                session_id=session_id,
                            )
                            num_events = len(existing_session.events)
                            logger.debug(f"Session found with {num_events} events")
                        except Exception:
                            logger.debug("Creating new session")
                            try:
                                await runner.session_service.create_session(
                                    app_name=agent_name,
                                    user_id=user_id,
                                    session_id=session_id,
                                )
                                # Get the newly created session
                                await runner.session_service.get_session(
                                    app_name=agent_name,
                                    user_id=user_id,
                                    session_id=session_id,
                                )
                            except Exception as create_error:
                                logger.error(
                                    f"Failed to create session: {create_error}"
                                )
                                raise create_error

                        # Session is ready for processing

                        responses = []
                        event_count = 0

                        # Import RunConfig and StreamingMode exactly like ADK web
                        from google.adk.agents.run_config import (
                            RunConfig,
                            StreamingMode,
                        )

                        # Call runner.run_async exactly like ADK web does in
                        # /run_sse endpoint
                        async for event in runner.run_async(
                            user_id=user_id,
                            session_id=session_id,
                            new_message=user_content,  # Key - pass the Content
                            state_delta=None,  # No state delta for simple case
                            run_config=RunConfig(
                                streaming_mode=StreamingMode.NONE
                            ),  # Like ADK web
                        ):
                            event_count += 1
                            await self._process_event_async(event, responses)

                        return responses, event_count

                    # Run the async call
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    responses, event_count = loop.run_until_complete(run_agent())
                    logger.debug(
                        f"Completed processing {event_count} events, "
                        f"{len(responses)} responses"
                    )
                    response = (
                        "\n".join(responses) if responses else "No response from agent"
                    )

                except Exception as e:
                    logger.error(f"Error in runner async call: {e}")
                    raise

                logger.info(f"Successfully generated response from {agent_name} agent")
                return str(response)

            except Exception as agent_error:
                error_msg = str(agent_error)
                logger.error(f"Agent call failed for {agent_name}: {error_msg}")
                logger.debug(f"Agent {agent_name} type: {type(agent)}")
                available_attrs = [
                    attr for attr in dir(agent) if not attr.startswith("_")
                ]
                logger.debug(f"Agent {agent_name} available methods: {available_attrs}")

                # Fallback response when agent integration isn't available
                ellipsis = "..." if len(message) > 50 else ""
                agent_title = agent_name.replace("_", " ").title()
                error_str = str(agent_error)
                return (
                    f"🤖 {agent_title} Agent: I received your message "
                    f"'{message[:50]}{ellipsis}'.\n\n⚠️ Agent Error: "
                    f"{error_str}\n\nThis indicates the agent integration "
                    "needs to be updated for the correct Google ADK API."
                )

        except Exception as e:
            error_str = str(e)
            logger.error(f"Error getting response from {agent_name}: {error_str}")
            return (
                "❌ Sorry, I encountered an error while processing your "
                f"request: {error_str}"
            )

    async def _process_event_async(self, event, responses):
        """Process a single event from the agent runner"""
        try:
            # Log function calls for debugging
            if hasattr(event, "get_function_calls"):
                function_calls = event.get_function_calls()
                if function_calls:
                    logger.debug(f"Function calls: {function_calls}")

            # Log function responses for debugging
            if hasattr(event, "get_function_responses"):
                function_responses = event.get_function_responses()
                if function_responses:
                    logger.debug(f"Function responses: {function_responses}")

            # Extract text content from the event
            event_text = self._extract_text_from_event(event)

            if event_text:
                responses.append(event_text)

        except Exception as e:
            logger.error(f"Error processing event: {e}")
            responses.append(f"Error processing response: {str(e)}")

    def _extract_text_from_event(self, event):
        """Extract text content from various ADK Event structures"""
        # Check if it's an LLM response event with actions
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

        # Check if event itself has content
        if hasattr(event, "content") and event.content:
            if hasattr(event.content, "parts"):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        return part.text
            elif hasattr(event.content, "text"):
                return event.content.text
            else:
                return str(event.content)

        # Check if event has direct text attribute
        elif hasattr(event, "text") and event.text:
            return event.text

        return None

    def get_primary_agent(self) -> str:
        """Get the primary agent (supervisor or demo fallback)"""
        if "supervisor" in self.agents:
            return "supervisor"
        else:
            return "demo"


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
    else:
        logger.debug("Using existing ChatbotManager from session state")

    # No need for agent selection anymore - using supervisor only

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = f"chat_{int(time.time())}"


def render_sidebar():
    """Render the sidebar with settings and controls"""
    with st.sidebar:
        st.title("🏠 Home Agent Suite")
        st.markdown("---")

        # Agent status
        st.subheader("🤖 Intelligent Agent")

        primary_agent = st.session_state.chatbot_manager.get_primary_agent()
        if primary_agent == "supervisor":
            st.success("🧠 **Supervisor Agent Active**")
            st.markdown(
                """
            The supervisor agent intelligently routes your queries to:
            - 🌤️ **Weather & Planning** for forecasts and activities
            - 🔍 **Web Search** for information and research
            """
            )
        else:
            st.warning("🎭 **Demo Mode**")
            st.markdown("Using demo agent - check configuration for full functionality")

        st.markdown("---")

        # Conversation controls
        st.subheader("💬 Conversation")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = [
                    st.session_state.messages[0]
                ]  # Keep welcome message
                st.session_state.conversation_id = f"chat_{int(time.time())}"
                st.rerun()

        with col2:
            if st.button("📥 Export Chat", use_container_width=True):
                export_chat_history()

        st.markdown("---")

        # Statistics
        st.subheader("📊 Statistics")
        message_count = len(
            [msg for msg in st.session_state.messages if msg["role"] == "user"]
        )
        st.metric("Messages Sent", message_count)
        st.metric("Conversation ID", st.session_state.conversation_id[-8:])

        st.markdown("---")

        # Information
        st.subheader("ℹ️ About")
        st.markdown(
            """
        This chatbot integrates with:
        - **Day Planner Agent**: Weather-based activity planning
        - **Google Search Agent**: Real-time information retrieval

        Built with Streamlit and Google ADK.
        """
        )


def export_chat_history():
    """Export chat history as JSON"""
    try:
        chat_data = {
            "conversation_id": st.session_state.conversation_id,
            "export_timestamp": datetime.now().isoformat(),
            "message_count": len(st.session_state.messages),
            "messages": st.session_state.messages,
        }

        json_string = json.dumps(chat_data, indent=2, ensure_ascii=False)

        st.download_button(
            label="💾 Download Chat History",
            data=json_string,
            file_name=f"chat_history_{st.session_state.conversation_id}.json",
            mime="application/json",
            use_container_width=True,
        )

        st.success("✅ Chat history prepared for download!")

    except Exception as e:
        st.error(f"❌ Error exporting chat history: {str(e)}")


def show_typing_indicator():
    """Show typing indicator while processing"""
    typing_placeholder = st.empty()
    with typing_placeholder.container():
        st.markdown(
            """
        <div class="typing-indicator">
            <span>🤖 Assistant is typing</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    time.sleep(1.5)  # Simulate processing time
    typing_placeholder.empty()


def render_chat_interface():
    """Render the main chat interface"""
    st.title("💬 Home Agent Chat")
    st.markdown("Ask me about day planning, weather insights, or general questions!")

    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        agent = message.get("agent", "unknown")
        timestamp = message.get("timestamp", "")

        # Format timestamp for display
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            time_display = dt.strftime("%H:%M")
        except Exception:
            time_display = ""

        # Determine avatar
        if role == "user":
            avatar = "👤"
        elif agent == "day_planner":
            avatar = "🗓️"
        elif agent == "google_search":
            avatar = "🔍"
        else:
            avatar = "🤖"

        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
            if time_display:
                st.caption(f"⏰ {time_display}")


def handle_user_input():
    """Handle user input and generate response"""
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat(),
            "agent": "user",
        }
        st.session_state.messages.append(user_message)

        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Show typing indicator
        with st.chat_message("assistant", avatar="🤖"):
            show_typing_indicator()

            # Use the primary agent (supervisor or demo)
            selected_agent = st.session_state.chatbot_manager.get_primary_agent()

            # Get response from agent
            response = st.session_state.chatbot_manager.get_agent_response(
                selected_agent, prompt
            )

            # Display response
            st.markdown(response)

            # Add assistant message to chat
            assistant_message = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "agent": selected_agent,
            }
            st.session_state.messages.append(assistant_message)

            # Show timestamp
            agent_title = selected_agent.replace("_", " ").title()
            timestamp = datetime.now().strftime("%H:%M")
            st.caption(f"⏰ {timestamp} • Agent: {agent_title}")


def main():
    """Main application function"""
    try:
        # Load custom CSS
        load_custom_css()

        # Initialize session state
        initialize_session_state()

        # Render sidebar
        render_sidebar()

        # Render main chat interface
        render_chat_interface()

        # Handle user input
        handle_user_input()

        logger.info("Streamlit chatbot application rendered successfully")

    except Exception as e:
        logger.error(f"Error in main application: {str(e)}")
        st.error(f"❌ Application Error: {str(e)}")
        st.info("Please refresh the page or contact support if the issue persists.")


if __name__ == "__main__":
    main()
