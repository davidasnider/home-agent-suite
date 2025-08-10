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
from typing import Dict, List, Any, Optional
import asyncio
from io import StringIO
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import existing agents with error handling
try:
    from agents.day_planner.agent import create_day_planner_agent
    DAY_PLANNER_AVAILABLE = True
except Exception as e:
    DAY_PLANNER_AVAILABLE = False
    day_planner_error = str(e)

try:
    from agents.google_search_agent.agent import create_google_search_agent
    GOOGLE_SEARCH_AVAILABLE = True
except Exception as e:
    GOOGLE_SEARCH_AVAILABLE = False
    google_search_error = str(e)

from common_logging.logging_utils import setup_logging

# Initialize logging
setup_logging(service_name="streamlit_chatbot")
logger = logging.getLogger(__name__) # TODO don't use __name__ give it a better name
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
        "About": "Home Agent Suite - Intelligent home automation and planning assistant"
    }
)

# Custom CSS for enhanced styling
def load_custom_css():
    """Load custom CSS for enhanced styling"""
    st.markdown("""
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
    """, unsafe_allow_html=True)

class ChatbotManager:
    """Manages chatbot agents and conversation state"""
    
    def __init__(self):
        self.agents = {}
        self.runners = {}  # Store runners to maintain session state
        
        # Initialize available agents
        if DAY_PLANNER_AVAILABLE:
            try:
                self.agents["day_planner"] = create_day_planner_agent()
                logger.info("Day planner agent initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize day planner agent: {e}")
        else:
            logger.warning(f"Day planner agent not available: {day_planner_error}")
            
        if GOOGLE_SEARCH_AVAILABLE:
            try:
                self.agents["google_search"] = create_google_search_agent()
                logger.info("Google search agent initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google search agent: {e}")
        else:
            logger.warning(f"Google search agent not available: {google_search_error}")
        
        # Add mock agent if no real agents are available
        if not self.agents:
            self.agents["demo"] = self._create_demo_agent()
            logger.info("No real agents available, using demo agent")
            
        logger.info("Chatbot manager initialized with %d agents", len(self.agents))
    
    def _create_demo_agent(self):
        """Create a demo agent for when real agents aren't available"""
        class DemoAgent:
            def __init__(self):
                self.name = "Demo Agent"
            
            def chat(self, message):
                return f"🤖 Demo Agent Response: I received your message '{message}'. This is a demonstration of the chat interface. Real agent integration requires proper API keys and configuration."
        
        return DemoAgent()
    
    def get_agent_response(self, agent_name: str, message: str) -> str:
        """Get response from specified agent"""
        try:
            if agent_name not in self.agents:
                return f"❌ Agent '{agent_name}' not found. Available agents: {', '.join(self.agents.keys())}"
            
            agent = self.agents[agent_name]
            
            # Call the actual Google ADK agent
            try:
                # Debug: Log available methods on the agent
                logger.debug(f"Agent {agent_name} methods: {[method for method in dir(agent) if not method.startswith('_')]}")
                
                # Try Google ADK agent invocation with proper Runner (proper way)
                from google.adk.runners import InMemoryRunner
                from google.genai import types
                
                # Get or create a persistent runner for this agent
                if agent_name not in self.runners:
                    try:
                        # Use agent name as app_name to match adk web behavior
                        self.runners[agent_name] = InMemoryRunner(
                            agent=agent,
                            app_name=agent_name
                        )
                        logger.debug(f"Created new InMemoryRunner for {agent_name}")
                    except Exception as runner_error:
                        logger.debug(f"Failed to create Runner: {runner_error}, trying direct agent calls")
                        use_runner = False
                        runner = None
                    else:
                        use_runner = True
                        runner = self.runners[agent_name]
                else:
                    logger.debug(f"Using existing InMemoryRunner for {agent_name}")
                    use_runner = True
                    runner = self.runners[agent_name]
                
                if use_runner:
                    # Use the Runner with proper ADK Content object
                    try:
                        # Create proper Content object for the message
                        content = types.Content(parts=[types.Part.from_text(text=message)])
                        logger.debug(f"Created Content object: {content}")
                        
                        # Use consistent session ID from Streamlit session state (with fallback for testing)
                        user_id = "streamlit_user"
                        try:
                            session_id = st.session_state.conversation_id  # Use existing conversation ID
                        except AttributeError:
                            # Fallback for non-Streamlit contexts (testing)
                            session_id = "test_session"
                        
                        logger.debug(f"Using session_id: {session_id}, user_id: {user_id}")
                        
                        # DEBUG: Log agent configuration before runner invocation
                        logger.debug(f"🔍 RUNNER DEBUG - Agent name: {agent.name}")
                        logger.debug(f"🔍 RUNNER DEBUG - Agent model: {agent.model}")
                        logger.debug(f"🔍 RUNNER DEBUG - Agent tools count: {len(agent.tools)}")
                        logger.debug(f"🔍 RUNNER DEBUG - Agent instruction preview: {agent.instruction[:200]}...")
                        for i, tool in enumerate(agent.tools):
                            tool_name = getattr(tool, '__name__', str(tool))
                            logger.debug(f"🔍 RUNNER DEBUG - Tool {i}: {tool_name} - {tool}")
                        
                        # Create session if it doesn't exist
                        try:
                            existing_session = runner.session_service.get_session_sync(
                                app_name=agent_name,
                                user_id=user_id, 
                                session_id=session_id
                            )
                            logger.debug(f"🔍 Using existing session: {session_id} with {len(existing_session.events)} events")
                            # DEBUG: Log session history
                            for i, event in enumerate(existing_session.events):
                                if hasattr(event, 'content') and event.content:
                                    content_preview = str(event.content)[:100] if event.content else "None"
                                    logger.debug(f"🔍 Session event {i}: {content_preview}...")
                        except Exception as e:
                            # Session doesn't exist, create it
                            logger.debug(f"🔍 Creating new session: {session_id} (error: {e})")
                            runner.session_service.create_session_sync(
                                app_name=agent_name,
                                user_id=user_id, 
                                session_id=session_id
                            )
                        
                        # DEBUG: Check session state before calling runner
                        try:
                            current_session = runner.session_service.get_session_sync(
                                app_name=agent_name,
                                user_id=user_id,
                                session_id=session_id
                            )
                            logger.info(f"🔍 BEFORE RUNNER CALL - Session has {len(current_session.events)} events")
                            for i, event in enumerate(current_session.events):
                                if hasattr(event, 'content') and event.content:
                                    content_preview = str(event.content)[:100]
                                    logger.info(f"🔍 Pre-run Event {i}: {content_preview}...")
                        except Exception as e:
                            logger.info(f"🔍 Could not get session before run: {e}")
                        
                        # DEBUG: Log just before runner.run()
                        logger.debug(f"🚀 ABOUT TO CALL RUNNER.RUN")
                        logger.debug(f"🚀 Message being sent: {message}")
                        logger.debug(f"🚀 Content object: {content}")
                        
                        # Use regular runner.run() - synchronous method like adk web uses
                        responses = []
                        event_count = 0
                        for event in runner.run(
                            user_id=user_id,
                            session_id=session_id,
                            new_message=content
                        ):
                            event_count += 1
                            logger.debug(f"🎯 RUNNER EVENT {event_count}: {type(event)}")
                            self._process_event(event, responses)
                        
                        logger.debug(f"🎯 RUNNER COMPLETED - Total events: {event_count}, Responses: {len(responses)}")
                        response = '\n'.join(responses) if responses else "No response from agent"
                        
                    except Exception as e:
                        logger.error(f"Error in runner.run: {e}")
                        raise
                    
                else:
                    # If Runner creation failed, show an informative error
                    logger.error(f"Could not create InMemoryRunner for {agent_name}")
                    raise Exception(f"Failed to create ADK Runner for agent {agent_name}. This is required for proper agent execution.")
                    
                logger.info(f"Successfully generated response from {agent_name} agent")
                return str(response)
                
            except Exception as agent_error:
                logger.error(f"Agent call failed for {agent_name}: {str(agent_error)}")
                logger.debug(f"Agent {agent_name} type: {type(agent)}")
                logger.debug(f"Agent {agent_name} available methods: {[attr for attr in dir(agent) if not attr.startswith('_')]}")
                
                # Fallback response when agent integration isn't available
                ellipsis = "..." if len(message) > 50 else ""
                return f"🤖 {agent_name.replace('_', ' ').title()} Agent: I received your message '{message[:50]}{ellipsis}'.\n\n⚠️ Agent Error: {str(agent_error)}\n\nThis indicates the agent integration needs to be updated for the correct Google ADK API."
            
        except Exception as e:
            logger.error(f"Error getting response from {agent_name}: {str(e)}")
            return f"❌ Sorry, I encountered an error while processing your request: {str(e)}"
    
    def _process_event(self, event, responses):
        """Process a single event from the agent runner synchronously"""
        try:
            logger.debug(f"Received event type: {type(event)}")
            logger.debug(f"Event attributes: {[attr for attr in dir(event) if not attr.startswith('_')]}")
            
            # Check for function calls (tool usage) - this is what we want to see!
            if hasattr(event, 'get_function_calls'):
                function_calls = event.get_function_calls()
                if function_calls:
                    logger.debug(f"✅ Function calls in event: {function_calls}")
                else:
                    logger.debug("No function calls in this event")
            
            # Check for tool/function responses
            if hasattr(event, 'get_function_responses'):
                function_responses = event.get_function_responses()
                if function_responses:
                    logger.debug(f"✅ Function responses in event: {function_responses}")
            
            # Try to extract text content from various ADK Event structures
            event_text = None
            
            # Check if it's an LLM response event with actions
            if hasattr(event, 'actions') and event.actions:
                for action in event.actions:
                    logger.debug(f"Action type: {type(action)}, attributes: {[attr for attr in dir(action) if not attr.startswith('_')]}")
                    if hasattr(action, 'text') and action.text:
                        event_text = action.text
                        break
                    elif hasattr(action, 'content') and action.content:
                        # Check if content has parts with text
                        if hasattr(action.content, 'parts'):
                            for part in action.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    event_text = part.text
                                    break
                        else:
                            event_text = str(action.content)
                        break
            
            # Check if event itself has content (this is where the response is!)
            if hasattr(event, 'content') and event.content:
                logger.debug(f"Event content type: {type(event.content)}")
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            event_text = part.text
                            logger.debug(f"Found text in content.parts: {part.text[:100]}...")
                            break
                elif hasattr(event.content, 'text'):
                    event_text = event.content.text
                    logger.debug(f"Found text in content: {event.content.text[:100]}...")
                else:
                    event_text = str(event.content)
            
            # Check if event has direct text attribute
            elif hasattr(event, 'text') and event.text:
                event_text = event.text
            
            # Log what we found and add to responses
            if event_text:
                logger.debug(f"Extracted text: {event_text[:100]}...")
                responses.append(event_text)
            else:
                logger.debug(f"No text found in event. Event structure: {vars(event) if hasattr(event, '__dict__') else str(event)}")
        
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            responses.append(f"Error processing response: {str(e)}")

    async def _process_event_async(self, event, responses):
        """Process a single event from the agent runner asynchronously"""
        try:
            logger.debug(f"Received event type: {type(event)}")
            logger.debug(f"Event attributes: {[attr for attr in dir(event) if not attr.startswith('_')]}")
            
            # Check for function calls (tool usage) - this is what we want to see!
            if hasattr(event, 'get_function_calls'):
                function_calls = event.get_function_calls()
                if function_calls:
                    logger.debug(f"✅ Function calls in event: {function_calls}")
                else:
                    logger.debug("No function calls in this event")
            
            # Check for tool/function responses
            if hasattr(event, 'get_function_responses'):
                function_responses = event.get_function_responses()
                if function_responses:
                    logger.debug(f"✅ Function responses in event: {function_responses}")
            
            # Try to extract text content from various ADK Event structures
            event_text = None
            
            # Check if it's an LLM response event with actions
            if hasattr(event, 'actions') and event.actions:
                for action in event.actions:
                    logger.debug(f"Action type: {type(action)}, attributes: {[attr for attr in dir(action) if not attr.startswith('_')]}")
                    if hasattr(action, 'text') and action.text:
                        event_text = action.text
                        break
                    elif hasattr(action, 'content') and action.content:
                        # Check if content has parts with text
                        if hasattr(action.content, 'parts'):
                            for part in action.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    event_text = part.text
                                    break
                        else:
                            event_text = str(action.content)
                        break
            
            # Check if event itself has content (this is where the response is!)
            if hasattr(event, 'content') and event.content:
                logger.debug(f"Event content type: {type(event.content)}")
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            event_text = part.text
                            logger.debug(f"Found text in content.parts: {part.text[:100]}...")
                            break
                elif hasattr(event.content, 'text'):
                    event_text = event.content.text
                    logger.debug(f"Found text in content: {event.content.text[:100]}...")
                else:
                    event_text = str(event.content)
            
            # Check if event has direct text attribute
            elif hasattr(event, 'text') and event.text:
                event_text = event.text
            
            # Log what we found and add to responses
            if event_text:
                logger.debug(f"Extracted text: {event_text[:100]}...")
                responses.append(event_text)
            else:
                logger.debug(f"No text found in event. Event structure: {vars(event) if hasattr(event, '__dict__') else str(event)}")
        
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            responses.append(f"Error processing response: {str(e)}")
    
    def auto_select_agent(self, message: str) -> str:
        """Automatically select the best agent based on message content"""
        message_lower = message.lower()
        
        # Simple keyword-based routing
        if "day_planner" in self.agents and any(word in message_lower for word in ["weather", "plan", "day", "activity", "outdoor"]):
            return "day_planner"
        elif "google_search" in self.agents and any(word in message_lower for word in ["search", "find", "google", "research", "fact"]):
            return "google_search"
        else:
            # Return first available agent
            return next(iter(self.agents.keys())) if self.agents else "demo"

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I'm your Home Agent Suite assistant. I can help you with day planning based on weather forecasts and answer questions using web search. How can I assist you today?",
                "timestamp": datetime.now().isoformat(),
                "agent": "system"
            }
        ]
    
    if "chatbot_manager" not in st.session_state:
        st.session_state.chatbot_manager = ChatbotManager()
        logger.debug("Created new ChatbotManager in session state")
    else:
        logger.debug("Using existing ChatbotManager from session state")
    
    if "selected_agent" not in st.session_state:
        st.session_state.selected_agent = "auto"
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = f"chat_{int(time.time())}"

def render_sidebar():
    """Render the sidebar with settings and controls"""
    with st.sidebar:
        st.title("🏠 Home Agent Suite")
        st.markdown("---")
        
        # Agent selection
        st.subheader("🤖 Agent Selection")
        
        # Build agent options based on available agents
        agent_options = {"auto": "🧠 Auto-Select"}
        
        # Add available agents
        available_agents = st.session_state.chatbot_manager.agents.keys()
        for agent_name in available_agents:
            if agent_name == "day_planner":
                agent_options[agent_name] = "🗓️ Day Planner"
            elif agent_name == "google_search":
                agent_options[agent_name] = "🔍 Google Search"
            elif agent_name == "demo":
                agent_options[agent_name] = "🎭 Demo Agent"
            else:
                agent_options[agent_name] = f"🤖 {agent_name.replace('_', ' ').title()}"
        
        st.session_state.selected_agent = st.selectbox(
            "Choose an agent:",
            options=list(agent_options.keys()),
            format_func=lambda x: agent_options[x],
            index=list(agent_options.keys()).index(st.session_state.selected_agent)
        )
        
        st.markdown("---")
        
        # Conversation controls
        st.subheader("💬 Conversation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = [st.session_state.messages[0]]  # Keep welcome message
                st.session_state.conversation_id = f"chat_{int(time.time())}"
                st.rerun()
        
        with col2:
            if st.button("📥 Export Chat", use_container_width=True):
                export_chat_history()
        
        st.markdown("---")
        
        # Statistics
        st.subheader("📊 Statistics")
        message_count = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
        st.metric("Messages Sent", message_count)
        st.metric("Conversation ID", st.session_state.conversation_id[-8:])
        
        st.markdown("---")
        
        # Information
        st.subheader("ℹ️ About")
        st.markdown("""
        This chatbot integrates with:
        - **Day Planner Agent**: Weather-based activity planning
        - **Google Search Agent**: Real-time information retrieval
        
        Built with Streamlit and Google ADK.
        """)

def export_chat_history():
    """Export chat history as JSON"""
    try:
        chat_data = {
            "conversation_id": st.session_state.conversation_id,
            "export_timestamp": datetime.now().isoformat(),
            "message_count": len(st.session_state.messages),
            "messages": st.session_state.messages
        }
        
        json_string = json.dumps(chat_data, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="💾 Download Chat History",
            data=json_string,
            file_name=f"chat_history_{st.session_state.conversation_id}.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.success("✅ Chat history prepared for download!")
        
    except Exception as e:
        st.error(f"❌ Error exporting chat history: {str(e)}")

def show_typing_indicator():
    """Show typing indicator while processing"""
    typing_placeholder = st.empty()
    with typing_placeholder.container():
        st.markdown("""
        <div class="typing-indicator">
            <span>🤖 Assistant is typing</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_display = dt.strftime("%H:%M")
        except:
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
            "agent": "user"
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Show typing indicator
        with st.chat_message("assistant", avatar="🤖"):
            show_typing_indicator()
            
            # Determine which agent to use
            if st.session_state.selected_agent == "auto":
                selected_agent = st.session_state.chatbot_manager.auto_select_agent(prompt)
            else:
                selected_agent = st.session_state.selected_agent
            
            # Get response from agent
            response = st.session_state.chatbot_manager.get_agent_response(selected_agent, prompt)
            
            # Display response
            st.markdown(response)
            
            # Add assistant message to chat
            assistant_message = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "agent": selected_agent
            }
            st.session_state.messages.append(assistant_message)
            
            # Show timestamp
            st.caption(f"⏰ {datetime.now().strftime('%H:%M')} • Agent: {selected_agent.replace('_', ' ').title()}")

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