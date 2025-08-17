"""
Comprehensive tests for common_logging.logging_utils module.

Tests cover error handling, environment detection, GCP integration,
and edge cases to achieve 90%+ code coverage.
"""

import logging
import os
from unittest.mock import patch, MagicMock
import pytest

from common_logging.logging_utils import setup_logging


class TestSetupLogging:
    """Test suite for setup_logging function."""

    def setup_method(self):
        """Reset logging state before each test."""
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.setLevel(logging.WARNING)

    def test_setup_logging_basic_local(self):
        """Test basic local logging setup without service name."""
        with patch.dict(os.environ, {}, clear=True):
            setup_logging()

        logger = logging.getLogger()
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1

    def test_setup_logging_with_service_name_local(self):
        """Test local logging setup with service name."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("logging.info") as mock_info:
                setup_logging(service_name="test_service")

                mock_info.assert_any_call("Service: test_service")
                mock_info.assert_any_call(
                    "Logging setup completed for service: %s", "test_service"
                )

    def test_setup_logging_no_service_name_local(self):
        """Test local logging setup without service name."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("logging.info") as mock_info:
                setup_logging()

                mock_info.assert_any_call(
                    "Logging setup completed for service: %s", "unknown"
                )

    def test_cloud_environment_detection_auto(self):
        """Test automatic cloud environment detection."""
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
            with patch("logging.debug") as mock_debug:
                with patch("google.cloud.logging.Client") as mock_client:
                    mock_client_instance = MagicMock()
                    mock_client.return_value = mock_client_instance

                    setup_logging()

                    mock_debug.assert_called_with(
                        "Cloud environment detected (GOOGLE_CLOUD_PROJECT set)"
                    )

    def test_local_environment_detection_auto(self):
        """Test automatic local environment detection."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("logging.debug") as mock_debug:
                setup_logging()

                mock_debug.assert_called_with(
                    "Local environment detected (no GOOGLE_CLOUD_PROJECT)"
                )

    def test_force_cloud_mode(self):
        """Test forcing cloud mode regardless of environment."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("google.cloud.logging.Client") as mock_client:
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance

                setup_logging(cloud=True)

                mock_client.assert_called_once()
                mock_client_instance.setup_logging.assert_called_once()

    def test_force_local_mode(self):
        """Test forcing local mode regardless of environment."""
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
            with patch("logging.info") as mock_info:
                setup_logging(cloud=False)

                mock_info.assert_any_call("Local console logging configured")

    def test_cloud_logging_success(self):
        """Test successful cloud logging setup."""
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
            with patch("google.cloud.logging.Client") as mock_client:
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance

                with patch("logging.info") as mock_info:
                    setup_logging()

                    mock_client.assert_called_once()
                    mock_client_instance.setup_logging.assert_called_once()
                    mock_info.assert_any_call(
                        "Cloud Logging handler attached successfully"
                    )

    def test_cloud_logging_client_exception(self):
        """Test handling of exceptions during cloud client setup."""
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
            with patch("google.cloud.logging.Client") as mock_client:
                mock_client.side_effect = Exception("Client setup failed")

                with patch("logging.basicConfig"):
                    with pytest.raises(Exception, match="Client setup failed"):
                        setup_logging()

    def test_handler_removal(self):
        """Test that existing handlers are properly removed."""
        logger = logging.getLogger()
        initial_handler = logging.StreamHandler()
        logger.addHandler(initial_handler)
        initial_count = len(logger.handlers)

        assert initial_count >= 1
        assert initial_handler in logger.handlers

        with patch.dict(os.environ, {}, clear=True):
            setup_logging()

        assert initial_handler not in logger.handlers

    def test_log_level_set_correctly(self):
        """Test that log level is set to INFO."""
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        with patch.dict(os.environ, {}, clear=True):
            setup_logging()

        assert logger.level == logging.INFO

    def test_service_name_with_none_value(self):
        """Test handling of None service name."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("logging.info") as mock_info:
                setup_logging(service_name=None)

                mock_info.assert_any_call(
                    "Logging setup completed for service: %s", "unknown"
                )

    def test_service_name_with_empty_string(self):
        """Test handling of empty string service name."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("logging.info") as mock_info:
                setup_logging(service_name="")

                # Empty string is falsy, so it becomes "unknown"
                mock_info.assert_any_call(
                    "Logging setup completed for service: %s", "unknown"
                )
                # Empty string service name should not trigger the "Service:" message
                service_calls = [
                    call_obj
                    for call_obj in mock_info.call_args_list
                    if len(call_obj[0]) > 0 and "Service:" in str(call_obj[0][0])
                ]
                assert len(service_calls) == 0

    def test_service_name_with_special_characters(self):
        """Test handling of service names with special characters."""
        special_name = "test-service_123.agent"
        with patch.dict(os.environ, {}, clear=True):
            with patch("logging.info") as mock_info:
                setup_logging(service_name=special_name)

                mock_info.assert_any_call(f"Service: {special_name}")

    def test_multiple_setup_calls(self):
        """Test that multiple setup calls work correctly."""
        with patch.dict(os.environ, {}, clear=True):
            setup_logging(service_name="first")
            setup_logging(service_name="second")

        logger = logging.getLogger()
        assert logger.level == logging.INFO

    def test_cloud_logging_setup_logging_exception(self):
        """Test handling of exceptions in cloud client setup_logging method."""
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
            with patch("google.cloud.logging.Client") as mock_client:
                mock_client_instance = MagicMock()
                mock_client_instance.setup_logging.side_effect = Exception(
                    "Setup failed"
                )
                mock_client.return_value = mock_client_instance

                with pytest.raises(Exception, match="Setup failed"):
                    setup_logging()

    def test_environment_variable_edge_cases(self):
        """Test edge cases for environment variable handling."""
        test_cases = [
            ("", False),
            ("0", True),
            ("false", True),
            ("null", True),
            ("test-project", True),
        ]

        for env_value, expected_cloud in test_cases:
            with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": env_value}):
                with patch("google.cloud.logging.Client") as mock_client:
                    mock_client_instance = MagicMock()
                    mock_client.return_value = mock_client_instance

                    if expected_cloud:
                        setup_logging()
                        mock_client.assert_called()
                    else:
                        with patch("logging.basicConfig"):
                            setup_logging()

    def test_debug_logging_messages(self):
        """Test that debug messages are properly logged."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("logging.debug") as mock_debug:
                setup_logging()

                mock_debug.assert_called_with(
                    "Local environment detected (no GOOGLE_CLOUD_PROJECT)"
                )

        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test"}):
            with patch("logging.debug") as mock_debug:
                with patch("google.cloud.logging.Client"):
                    setup_logging()

                    mock_debug.assert_called_with(
                        "Cloud environment detected (GOOGLE_CLOUD_PROJECT set)"
                    )

    def test_basic_config_format_local(self):
        """Test that basicConfig is called with correct format for local."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("logging.basicConfig") as mock_basic:
                setup_logging()

                expected_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
                expected_level = logging.INFO

                # Check that basicConfig was called with the right arguments
                mock_basic.assert_called()
                call_args = mock_basic.call_args
                if call_args and call_args[1]:
                    assert call_args[1].get("format") == expected_format
                    assert call_args[1].get("level") == expected_level

    def test_cloud_parameter_override(self):
        """Test that cloud parameter overrides environment detection."""
        # Test forcing local mode when cloud env is set
        with patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "test-project"}):
            with patch("logging.basicConfig") as mock_basic:
                with patch("logging.info") as mock_info:
                    setup_logging(cloud=False)

                    mock_basic.assert_called()
                    mock_info.assert_any_call("Local console logging configured")

        # Test forcing cloud mode when no cloud env
        with patch.dict(os.environ, {}, clear=True):
            with patch("google.cloud.logging.Client") as mock_client:
                mock_client_instance = MagicMock()
                mock_client.return_value = mock_client_instance

                setup_logging(cloud=True)

                mock_client.assert_called_once()


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def setup_method(self):
        """Reset logging state before each test."""
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.setLevel(logging.WARNING)

    def test_actual_logging_after_setup_local(self):
        """Test that actual logging works after setup in local mode."""
        with patch.dict(os.environ, {}, clear=True):
            setup_logging(service_name="integration_test")

            logger = logging.getLogger("test.module")

            with patch("sys.stderr"):
                logger.info("Test message")

    def test_logging_hierarchy_preserved(self):
        """Test that logging hierarchy is preserved after setup."""
        with patch.dict(os.environ, {}, clear=True):
            setup_logging()

            root_logger = logging.getLogger()
            child_logger = logging.getLogger("child")
            grandchild_logger = logging.getLogger("child.grandchild")

            assert child_logger.parent == root_logger
            assert grandchild_logger.parent == child_logger

    def test_log_level_inheritance(self):
        """Test that log level inheritance works correctly."""
        with patch.dict(os.environ, {}, clear=True):
            setup_logging()

            child_logger = logging.getLogger("child")

            assert child_logger.getEffectiveLevel() == logging.INFO
