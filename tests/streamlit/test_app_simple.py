"""
Simple, focused tests for app.py targeting high coverage.

Tests the functions that can be easily tested without complex mocking.
"""

from unittest.mock import Mock, patch
import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestModuleLevel:
    """Test module-level functionality."""

    def test_module_imports(self):
        """Test that the module imports successfully."""
        import app

        # Basic checks
        assert hasattr(app, "ChatbotManager")
        assert hasattr(app, "main")
        assert hasattr(app, "load_custom_css")
        assert hasattr(app, "export_chat_history")
        assert hasattr(app, "show_typing_indicator")


class TestCSS:
    """Test CSS loading."""

    @patch("streamlit.markdown")
    def test_load_custom_css(self, mock_markdown):
        """Test CSS loading function."""
        from app import load_custom_css

        load_custom_css()

        mock_markdown.assert_called_once()
        args, kwargs = mock_markdown.call_args

        css_content = args[0]
        assert "<style>" in css_content
        assert ".stChatMessage" in css_content
        assert kwargs.get("unsafe_allow_html") is True


class TestExport:
    """Test export functionality."""

    @patch("streamlit.session_state")
    @patch("streamlit.download_button")
    @patch("streamlit.success")
    def test_export_success(self, mock_success, mock_download, mock_session_state):
        """Test successful export."""
        mock_session_state.conversation_id = "test_123"
        mock_session_state.messages = [
            {"role": "user", "content": "Hi", "timestamp": "2025-08-17T10:00:00Z"}
        ]

        from app import export_chat_history

        export_chat_history()

        mock_download.assert_called_once()
        mock_success.assert_called_once()

        # Check download data
        call_kwargs = mock_download.call_args[1]
        json_data = json.loads(call_kwargs["data"])
        assert json_data["conversation_id"] == "test_123"
        assert json_data["message_count"] == 1

    @patch("streamlit.session_state", {})
    @patch("streamlit.error")
    def test_export_error(self, mock_error):
        """Test export error handling."""
        from app import export_chat_history

        export_chat_history()

        mock_error.assert_called_once()
        error_msg = mock_error.call_args[0][0]
        assert "Error exporting chat history" in error_msg


class TestTypingIndicator:
    """Test typing indicator."""

    @patch("streamlit.empty")
    @patch("time.sleep")
    def test_show_typing_indicator(self, mock_sleep, mock_empty):
        """Test typing indicator functionality."""
        mock_placeholder = Mock()
        mock_empty.return_value = mock_placeholder

        # Setup container context manager
        mock_container = Mock()
        mock_placeholder.container.return_value.__enter__ = Mock(
            return_value=mock_container
        )
        mock_placeholder.container.return_value.__exit__ = Mock(return_value=None)

        from app import show_typing_indicator

        show_typing_indicator()

        mock_empty.assert_called_once()
        mock_sleep.assert_called_once_with(1.5)
        mock_placeholder.empty.assert_called_once()


class TestMainFunction:
    """Test main function."""

    @patch("app.handle_user_input")
    @patch("app.render_chat_interface")
    @patch("app.render_sidebar")
    @patch("app.initialize_session_state")
    @patch("app.load_custom_css")
    @patch("app.logger")
    def test_main_success(
        self, mock_logger, mock_css, mock_init, mock_sidebar, mock_chat, mock_input
    ):
        """Test successful main execution."""
        from app import main

        main()

        # All functions should be called
        mock_css.assert_called_once()
        mock_init.assert_called_once()
        mock_sidebar.assert_called_once()
        mock_chat.assert_called_once()
        mock_input.assert_called_once()

    @patch("app.handle_user_input")
    @patch("app.render_chat_interface")
    @patch("app.render_sidebar")
    @patch("app.initialize_session_state")
    @patch("app.load_custom_css")
    @patch("streamlit.error")
    @patch("streamlit.info")
    @patch("app.logger")
    def test_main_error(
        self,
        mock_logger,
        mock_info,
        mock_error,
        mock_css,
        mock_init,
        mock_sidebar,
        mock_chat,
        mock_input,
    ):
        """Test main function error handling."""
        from app import main

        # Make a function fail
        mock_css.side_effect = Exception("CSS error")

        main()

        mock_error.assert_called_once()
        mock_info.assert_called_once()

        error_msg = mock_error.call_args[0][0]
        assert "Application Error" in error_msg


class TestSessionState:
    """Test session state functions."""

    # Note: Session state testing is complex due to Streamlit's internal structure
    # Would require extensive mocking of st.session_state and ChatbotManager
    pass


class TestChatInterface:
    """Test chat interface functions with minimal mocking."""

    @patch("streamlit.session_state")
    @patch("streamlit.title")
    @patch("streamlit.markdown")
    @patch("streamlit.chat_message")
    def test_render_chat_interface(
        self, mock_chat_message, mock_markdown, mock_title, mock_session_state
    ):
        """Test chat interface rendering."""
        mock_session_state.messages = [
            {
                "role": "user",
                "content": "Hello",
                "timestamp": "2025-08-17T10:00:00Z",
                "agent": "user",
            }
        ]

        # Mock chat message context manager
        mock_context = Mock()
        mock_chat_message.return_value.__enter__ = Mock(return_value=mock_context)
        mock_chat_message.return_value.__exit__ = Mock(return_value=None)

        from app import render_chat_interface

        render_chat_interface()

        mock_title.assert_called_once()
        mock_markdown.assert_called()
        mock_chat_message.assert_called()


class TestSidebar:
    """Test sidebar functionality."""

    @patch("streamlit.session_state")
    @patch("streamlit.sidebar")
    def test_render_sidebar_basic(self, mock_sidebar, mock_session_state):
        """Test basic sidebar rendering."""
        # Setup session state
        mock_manager = Mock()
        mock_manager.get_primary_agent.return_value = "supervisor"
        mock_session_state.chatbot_manager = mock_manager
        mock_session_state.messages = []
        mock_session_state.conversation_id = "test_123"

        # Mock sidebar context manager
        mock_sidebar.__enter__ = Mock()
        mock_sidebar.__exit__ = Mock()

        from app import render_sidebar

        render_sidebar()

        # Should check primary agent
        mock_manager.get_primary_agent.assert_called()


class TestUserInput:
    """Test user input handling."""

    @patch("streamlit.session_state")
    @patch("streamlit.chat_input")
    @patch("streamlit.chat_message")
    @patch("app.show_typing_indicator")
    def test_handle_user_input_no_input(
        self, mock_typing, mock_chat_message, mock_chat_input, mock_session_state
    ):
        """Test handling when no user input."""
        mock_session_state.messages = []
        mock_chat_input.return_value = None  # No input

        from app import handle_user_input

        handle_user_input()

        # Should not add any messages
        assert len(mock_session_state.messages) == 0
        mock_typing.assert_not_called()

    @patch("streamlit.session_state")
    @patch("streamlit.chat_input")
    @patch("streamlit.chat_message")
    @patch("app.show_typing_indicator")
    def test_handle_user_input_with_input(
        self, mock_typing, mock_chat_message, mock_chat_input, mock_session_state
    ):
        """Test handling with user input."""
        mock_manager = Mock()
        mock_manager.get_primary_agent.return_value = "supervisor"
        mock_manager.get_agent_response.return_value = "Test response"

        mock_session_state.messages = []
        mock_session_state.chatbot_manager = mock_manager
        mock_session_state.last_request_time = 0
        mock_chat_input.return_value = "Test message"

        # Mock chat message context manager
        mock_context = Mock()
        mock_chat_message.return_value.__enter__ = Mock(return_value=mock_context)
        mock_chat_message.return_value.__exit__ = Mock(return_value=None)

        from app import handle_user_input

        handle_user_input()

        # Should add user and assistant messages
        assert len(mock_session_state.messages) == 2
        assert mock_session_state.messages[0]["role"] == "user"
        assert mock_session_state.messages[0]["content"] == "Test message"
        assert mock_session_state.messages[1]["role"] == "assistant"
        assert mock_session_state.messages[1]["content"] == "Test response"

        mock_typing.assert_called_once()
        mock_manager.get_agent_response.assert_called_once_with(
            "supervisor", "Test message"
        )

    @patch("streamlit.session_state")
    @patch("streamlit.chat_input")
    @patch("streamlit.toast")
    def test_handle_user_input_rate_limited(
        self, mock_toast, mock_chat_input, mock_session_state
    ):
        """Test that rate limiting prevents frequent requests."""
        import time

        mock_session_state.last_request_time = time.time()
        mock_chat_input.return_value = "Test message"

        from app import handle_user_input

        handle_user_input()

        mock_toast.assert_called_once_with(
            "You are sending requests too quickly. Please wait a moment."
        )

    @patch("streamlit.session_state")
    @patch("streamlit.chat_input")
    @patch("streamlit.toast")
    def test_handle_user_input_too_long(
        self, mock_toast, mock_chat_input, mock_session_state
    ):
        """Test that long inputs are rejected."""
        mock_session_state.last_request_time = 0
        mock_chat_input.return_value = "a" * 1025

        from app import handle_user_input

        handle_user_input()

        mock_toast.assert_called_once_with(
            "Error: Input is too long. Please limit your query to 1024 characters."
        )

    @patch("streamlit.session_state")
    @patch("streamlit.chat_input")
    @patch("streamlit.chat_message")
    @patch("app.show_typing_indicator")
    def test_handle_user_input_sanitization(
        self, mock_typing, mock_chat_message, mock_chat_input, mock_session_state
    ):
        """Test that user input is sanitized."""
        mock_manager = Mock()
        mock_manager.get_primary_agent.return_value = "supervisor"
        mock_manager.get_agent_response.return_value = "Test response"
        mock_session_state.messages = []
        mock_session_state.chatbot_manager = mock_manager
        mock_session_state.last_request_time = 0
        mock_chat_input.return_value = "<script>alert('XSS')</script>"

        mock_context = Mock()
        mock_chat_message.return_value.__enter__ = Mock(return_value=mock_context)
        mock_chat_message.return_value.__exit__ = Mock(return_value=None)

        from app import handle_user_input

        handle_user_input()

        # Check that the sanitized message is passed to the agent
        sanitized_message = "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;"
        mock_manager.get_agent_response.assert_called_once_with(
            "supervisor", sanitized_message
        )
        assert mock_session_state.messages[0]["content"] == sanitized_message


# Test some edge cases to increase coverage
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_timestamp_parsing_in_render_chat_interface(self):
        """Test timestamp parsing handles various formats."""
        with (
            patch("streamlit.session_state") as mock_session_state,
            patch("streamlit.title"),
            patch("streamlit.markdown"),
            patch("streamlit.chat_message") as mock_chat_message,
        ):

            # Test with invalid timestamp
            mock_session_state.messages = [
                {
                    "role": "user",
                    "content": "Test",
                    "timestamp": "invalid-timestamp",
                    "agent": "user",
                }
            ]

            mock_context = Mock()
            mock_chat_message.return_value.__enter__ = Mock(return_value=mock_context)
            mock_chat_message.return_value.__exit__ = Mock(return_value=None)

            from app import render_chat_interface

            # Should not raise exception
            render_chat_interface()

    def test_avatar_selection_logic(self):
        """Test avatar selection for different agents."""
        with (
            patch("streamlit.session_state") as mock_session_state,
            patch("streamlit.title"),
            patch("streamlit.markdown"),
            patch("streamlit.chat_message") as mock_chat_message,
        ):

            # Test different agent types
            mock_session_state.messages = [
                {"role": "user", "content": "Test", "agent": "user", "timestamp": ""},
                {
                    "role": "assistant",
                    "content": "Test",
                    "agent": "day_planner",
                    "timestamp": "",
                },
                {
                    "role": "assistant",
                    "content": "Test",
                    "agent": "google_search",
                    "timestamp": "",
                },
                {
                    "role": "assistant",
                    "content": "Test",
                    "agent": "supervisor",
                    "timestamp": "",
                },
            ]

            mock_context = Mock()
            mock_chat_message.return_value.__enter__ = Mock(return_value=mock_context)
            mock_chat_message.return_value.__exit__ = Mock(return_value=None)

            from app import render_chat_interface

            render_chat_interface()

            # Should call chat_message for each message
            assert mock_chat_message.call_count == 4
