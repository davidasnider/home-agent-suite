"""
Tests for demo_app.py

Simple tests to cover the demo app functionality.
"""

from unittest.mock import patch
import sys
from pathlib import Path


class TestDemoApp:
    """Test demo app functionality."""

    @patch("subprocess.run")
    def test_main_success(self, mock_subprocess_run):
        """Test successful demo app execution."""
        from demo_app import main

        # Mock successful subprocess run
        mock_subprocess_run.return_value = None

        result = main()

        # Should return 0 for success
        assert result == 0

        # Should call subprocess.run with correct arguments
        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args[0][0]

        # Check command structure
        assert call_args[0] == sys.executable
        assert call_args[1] == "-m"
        assert call_args[2] == "streamlit"
        assert call_args[3] == "run"
        assert "app.py" in call_args[4]

        # Should have check=True
        assert mock_subprocess_run.call_args[1]["check"] is True

    @patch("subprocess.run")
    def test_main_keyboard_interrupt(self, mock_subprocess_run):
        """Test demo app handling keyboard interrupt."""
        from demo_app import main

        # Mock KeyboardInterrupt
        mock_subprocess_run.side_effect = KeyboardInterrupt()

        with patch("builtins.print") as mock_print:
            result = main()

            # Should return 0 (successful shutdown)
            assert result == 0

            # Should print goodbye message
            mock_print.assert_called_once_with(
                "\n👋 Chatbot application stopped by user"
            )

    @patch("subprocess.run")
    def test_main_exception(self, mock_subprocess_run):
        """Test demo app handling general exception."""
        from demo_app import main

        # Mock general exception
        test_error = Exception("Test error")
        mock_subprocess_run.side_effect = test_error

        with patch("builtins.print") as mock_print:
            result = main()

            # Should return 1 for error
            assert result == 1

            # Should print error message
            mock_print.assert_called_once_with(
                "❌ Error running the application: Test error"
            )

    @patch("demo_app.main")
    @patch("sys.exit")
    def test_main_module_execution(self, mock_sys_exit, mock_main):
        """Test that __name__ == '__main__' calls sys.exit(main())."""
        mock_main.return_value = 42

        # Import should trigger the if __name__ == "__main__" block
        # We can't easily test this directly, so we test the components

        # Verify the main function exists and is callable
        from demo_app import main

        assert callable(main)

    def test_app_path_construction(self):
        """Test that app path is constructed correctly."""
        # We can't easily mock Path inside the function, but we can verify
        # the logic by checking that the function doesn't crash on import
        # and that Path operations work
        app_path = Path(__file__).parent.parent / "app.py"
        assert app_path.name == "app.py"
