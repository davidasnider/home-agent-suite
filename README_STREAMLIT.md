# Streamlit Chatbot Application

A modern, responsive chat interface for the Home Agent Suite that integrates with Google ADK agents for intelligent home automation and planning assistance.

## Features

✅ **Complete Implementation**:
- Modern UI using Streamlit's native chat components (`st.chat_message()`, `st.chat_input()`)
- Session state management for conversation persistence across page refreshes
- Integration with existing Day Planner and Google Search agents
- Professional, clean design with custom CSS styling
- Mobile-responsive layout with collapsible sidebar
- Message avatars (👤 for user, 🗓️ for day planner, 🔍 for search, 🤖 for system)
- Typing indicators with animated dots (`st.spinner()`)
- Clear chat history functionality
- Export chat history as JSON
- Error handling and loading states
- Auto-agent selection based on message content
- Manual agent selection via sidebar

## Quick Start

### 1. Run the Application

```bash
# Using Poetry (recommended)
poetry run streamlit run app.py

# Or using the demo script
poetry run python demo_app.py
```

### 2. Access the Interface

The application will open in your browser at `http://localhost:8501`

## Architecture

### Core Components

- **`app.py`** - Main Streamlit application with full functionality
- **`ChatbotManager`** - Handles agent initialization and message routing
- **Agent Integration** - Connects with existing Google ADK agents
- **Session Management** - Persists conversation history and state

### Agent Support

The chatbot automatically detects and integrates available agents:

- **🗓️ Day Planner Agent** - Weather-based activity planning (requires Tomorrow.io API key)
- **🔍 Google Search Agent** - Real-time web search and research
- **🎭 Demo Agent** - Fallback for when other agents aren't configured

### Smart Agent Routing

**Auto-Selection Logic:**
- Weather/planning keywords → Day Planner Agent
- Search/research keywords → Google Search Agent
- Manual selection available via sidebar

## UI/UX Features

### Modern Design Elements

- **Gradient backgrounds** for user messages
- **Accent borders** for assistant responses
- **Smooth animations** for buttons and interactions
- **Professional typography** with proper spacing
- **Color-coded avatars** for easy message identification

### Mobile Responsiveness

- Responsive layout that adapts to screen size
- Touch-friendly button sizes
- Collapsible sidebar on mobile
- Optimized message spacing

### Custom CSS Enhancements

```css
/* Examples of applied styling */
- Rounded message bubbles with shadows
- Gradient button effects with hover animations
- Animated typing indicators
- Responsive breakpoints for mobile
- Consistent color scheme throughout
```

## Configuration

### Environment Setup

**Required for full agent functionality:**

1. **Get Required API Keys:**

   **Tomorrow.io Weather API:**
   - Visit [Tomorrow.io Weather API](https://www.tomorrow.io/weather-api/)
   - Sign up for a free account
   - Copy your API key from the dashboard

   **Google AI API (for Gemini models):**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Create a new API key
   - Copy the generated API key

2. **Configure Environment Variables:**

   A `.env` file has been created for you. Edit it with your actual API keys:

   ```bash
   # Edit the .env file
   nano .env
   # or
   code .env
   ```

   Update the file with your real API keys:

   ```env
   # Tomorrow.io Weather API
   TOMORROW_IO_API_KEY=your_actual_tomorrow_io_key_here
   
   # Google AI API (for Gemini models)
   GOOGLE_API_KEY=your_actual_google_ai_key_here

   # Optional: Logging level
   LOG_LEVEL=INFO
   ```

   **Note:** Both API clients automatically load environment variables from `.env` files, so no additional configuration is needed in the application code.

3. **Verify Configuration:**

   ```bash
   # Test that the day planner agent loads correctly
   poetry run python3 -c "from agents.day_planner.agent import create_day_planner_agent; print('✅ Day Planner Agent loaded successfully!')"
   ```

   If successful, you'll see logging output and the success message. If it fails, check that both API keys are correct.

4. **Run the Application:**

   ```bash
   # Start the Streamlit chatbot
   poetry run streamlit run app.py
   ```

   **Safari HTTPS-Only Issue:** If Safari shows "Navigation failed" due to HTTPS-Only mode:
   - **Quick fix:** Safari Settings → Websites → HTTPS-Only → Set localhost to "Off"
   - **Alternative:** Use Chrome/Firefox: `open -a "Google Chrome" http://localhost:8501`

   With a valid API key, you'll now have access to:
   - 🗓️ **Day Planner Agent** - Weather-based activity recommendations  
   - 🔍 **Google Search Agent** - Web research capabilities
   - 🎭 **Demo Agent** - Fallback demonstration mode

### Without API Keys

If you don't have API keys configured:

- The application will still run with the **Google Search Agent** and **Demo Agent**
- The Day Planner Agent will be unavailable but won't break the application  
- You'll see helpful error messages in the UI indicating missing configuration
- The sidebar will only show available agents

### Dependencies

All dependencies are managed via Poetry:

```toml
[tool.poetry.dependencies]
streamlit = "^1.48.0"
google-adk = "^1.10.0"
python-dotenv = "^1.1.1"
```

## Usage Examples

### Basic Chat Interaction

1. Open the application
2. Type a message in the chat input
3. Watch the typing indicator
4. Receive response from the selected agent

### Agent Selection

**Auto-Selection:**
- "What's the weather like?" → Day Planner Agent
- "Search for Python tutorials" → Google Search Agent

**Manual Selection:**
- Use the sidebar dropdown to choose a specific agent
- Selection persists for the session

### Export Chat History

1. Click "📥 Export Chat" in the sidebar
2. Click "💾 Download Chat History" when prompted
3. Receive JSON file with full conversation

## Development

### Project Structure

```
home-agent-suite/
├── app.py                 # Main Streamlit application
├── demo_app.py           # Demo runner script
├── agents/               # Google ADK agents
│   ├── day_planner/      # Weather-based planning
│   └── google_search_agent/ # Web search
└── libs/                 # Shared libraries
    ├── common_logging/   # Logging utilities
    └── tomorrow_io_client/ # Weather API client
```

### Key Implementation Details

**Session State Management:**
```python
# Conversation persistence
st.session_state.messages = [...]
st.session_state.chatbot_manager = ChatbotManager()
st.session_state.selected_agent = "auto"
```

**Agent Integration Pattern:**
```python
# Graceful agent loading
try:
    agent = create_day_planner_agent()
    # Use agent.chat(message) or agent.process(message)
except Exception:
    # Fallback to demo mode
```

**Custom CSS Integration:**
```python
def load_custom_css():
    st.markdown("""<style>...</style>""", unsafe_allow_html=True)
```

## Troubleshooting

### Common Issues

1. **"Agent not found" errors**
   - Ensure API keys are configured in `.env`
   - Check agent initialization logs

2. **Import errors**
   - Run `poetry install` to ensure dependencies
   - Verify Python 3.11+ is being used

3. **Styling not applied**
   - Check browser developer tools
   - Ensure `unsafe_allow_html=True` is set

### Logging

Application logs include:
- Agent initialization status
- Message routing decisions  
- Error details and stack traces
- Performance metrics

## Future Enhancements

### Planned Features

- [ ] Voice input/output integration
- [ ] File upload and processing
- [ ] Multi-language support
- [ ] Advanced conversation analytics
- [ ] Custom agent creation interface
- [ ] Integration with more home automation systems

### Technical Improvements

- [ ] Async agent processing for better performance
- [ ] WebSocket integration for real-time updates
- [ ] Advanced caching for faster responses
- [ ] A/B testing framework for UI improvements

---

**Built with ❤️ using Streamlit and Google ADK**

For issues or feature requests, please create an issue in the GitHub repository.