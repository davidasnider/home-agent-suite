"""
Pytest fixtures for Streamlit app testing.

Provides mocked Streamlit components and test data for comprehensive
testing of the chatbot application.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit module and its components."""
    with patch("streamlit") as mock_st:
        # Mock session state
        mock_st.session_state = {}

        # Mock UI components
        mock_st.set_page_config = Mock()
        mock_st.title = Mock()
        mock_st.markdown = Mock()
        mock_st.sidebar = MagicMock()
        mock_st.chat_message = MagicMock()
        mock_st.chat_input = Mock()
        mock_st.button = Mock()
        mock_st.columns = Mock(return_value=[Mock(), Mock()])
        mock_st.empty = Mock()
        mock_st.success = Mock()
        mock_st.warning = Mock()
        mock_st.error = Mock()
        mock_st.info = Mock()
        mock_st.metric = Mock()
        mock_st.download_button = Mock()
        mock_st.subheader = Mock()
        mock_st.caption = Mock()
        mock_st.rerun = Mock()

        yield mock_st


@pytest.fixture
def sample_messages():
    """Sample chat messages for testing."""
    return [
        {
            "role": "assistant",
            "content": "Hello! I'm your assistant.",
            "timestamp": "2025-08-17T10:00:00.000Z",
            "agent": "supervisor",
        },
        {
            "role": "user",
            "content": "What's the weather like?",
            "timestamp": "2025-08-17T10:01:00.000Z",
            "agent": "user",
        },
        {
            "role": "assistant",
            "content": "The weather is sunny today.",
            "timestamp": "2025-08-17T10:01:30.000Z",
            "agent": "supervisor",
        },
    ]


@pytest.fixture
def mock_supervisor_agent():
    """Mock supervisor agent for testing."""
    mock_agent = Mock()
    mock_agent.name = "supervisor"
    return mock_agent


@pytest.fixture
def mock_demo_agent():
    """Mock demo agent for testing."""
    mock_agent = Mock()
    mock_agent.name = "Demo Agent"
    mock_agent.chat = Mock(return_value="Demo response")
    return mock_agent


@pytest.fixture
def mock_session_service():
    """Mock InMemorySessionService for testing."""
    mock_service = Mock()
    mock_service.get_session = Mock()
    mock_service.create_session = Mock()
    return mock_service


@pytest.fixture
def mock_runner():
    """Mock InMemoryRunner for testing agent execution."""
    mock_runner = Mock()
    mock_runner.session_service = Mock()

    # Mock async iterator for run_async
    async def mock_run_async(*args, **kwargs):
        # Yield mock events
        mock_event = Mock()
        mock_event.actions = []
        yield mock_event

    mock_runner.run_async = mock_run_async
    return mock_runner


@pytest.fixture
def mock_environment_variables():
    """Mock environment variables and imports."""
    with patch.dict(
        "os.environ",
        {
            "GOOGLE_API_KEY": "test_key",  # pragma: allowlist secret
            "TOMORROW_IO_API_KEY": "test_weather_key",  # pragma: allowlist secret
        },
    ):
        yield


@pytest.fixture
def mock_logging():
    """Mock logging to capture log messages during tests."""
    with patch("app.logger") as mock_logger:
        mock_logger.debug = Mock()
        mock_logger.info = Mock()
        mock_logger.warning = Mock()
        mock_logger.error = Mock()
        yield mock_logger


@pytest.fixture
def conversation_export_data():
    """Sample conversation data for export testing."""
    return {
        "conversation_id": "chat_1629123456",
        "export_timestamp": "2025-08-17T10:00:00.000Z",
        "message_count": 3,
        "messages": [
            {
                "role": "assistant",
                "content": "Hello! How can I help you?",
                "timestamp": "2025-08-17T09:58:00.000Z",
                "agent": "supervisor",
            },
            {
                "role": "user",
                "content": "Tell me about the weather",
                "timestamp": "2025-08-17T09:59:00.000Z",
                "agent": "user",
            },
            {
                "role": "assistant",
                "content": "The weather forecast shows sunny skies today.",
                "timestamp": "2025-08-17T10:00:00.000Z",
                "agent": "supervisor",
            },
        ],
    }


@pytest.fixture
def mock_adk_imports():
    """Mock Google ADK imports for testing."""
    with (
        patch(
            "google.adk.sessions.in_memory_session_service.InMemorySessionService"
        ) as mock_session,
        patch("google.adk.runners.InMemoryRunner") as mock_runner_class,
        patch("google.genai.types") as mock_types,
        patch("google.adk.agents.run_config") as mock_run_config,
    ):

        # Setup mock session service
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance

        # Setup mock runner
        mock_runner_instance = Mock()
        mock_runner_class.return_value = mock_runner_instance

        # Setup mock types
        mock_content = Mock()
        mock_part = Mock()
        mock_part.from_text.return_value = mock_part
        mock_content.parts = [mock_part]
        mock_types.Content.return_value = mock_content
        mock_types.Part = mock_part

        # Setup mock run config
        mock_run_config.RunConfig = Mock()
        mock_run_config.StreamingMode = Mock()
        mock_run_config.StreamingMode.NONE = "NONE"

        yield {
            "session_service": mock_session,
            "runner": mock_runner_class,
            "types": mock_types,
            "run_config": mock_run_config,
        }


@pytest.fixture
def mock_supervisor_import():
    """Mock supervisor agent import for testing."""
    with patch("supervisor.agent.create_supervisor_agent") as mock_create:
        mock_agent = Mock()
        mock_agent.name = "supervisor"
        mock_create.return_value = mock_agent
        yield mock_create, mock_agent


@pytest.fixture
def chatbot_manager_mocks(mock_adk_imports, mock_supervisor_import):
    """Combined fixture for ChatbotManager testing."""
    return {"adk": mock_adk_imports, "supervisor": mock_supervisor_import}
