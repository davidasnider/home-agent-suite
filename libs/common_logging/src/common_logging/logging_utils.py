"""
Common Logging Utilities Module

This module provides centralized logging configuration for the home-agent-suite
system, supporting both local development and Google Cloud Platform deployments.

The logging system automatically detects the runtime environment and configures
appropriate handlers, formatters, and log levels for optimal observability.

Key Features:
- Automatic cloud/local environment detection
- Google Cloud Logging integration
- Consistent log formatting across services
- Structured logging for better searchability

For MCP and agentic AI systems, this module:
- Provides standardized logging interfaces
- Enables distributed tracing capabilities
- Supports audit trails for agent interactions
- Facilitates debugging across service boundaries
"""

import logging
import os
import re
from typing import Optional


class RedactingFilter(logging.Filter):
    """A logging filter that redacts sensitive information."""

    def __init__(self, patterns, name: str = ""):
        super().__init__(name)
        self._patterns = [(re.compile(p), "[REDACTED]") for p in patterns]

    def filter(self, record):
        record.msg = self._redact(record.msg)
        if isinstance(record.args, dict):
            for k in record.args.keys():
                record.args[k] = self._redact(record.args[k])
        else:
            record.args = tuple(self._redact(arg) for arg in record.args)
        return True

    def _redact(self, msg):
        if isinstance(msg, str):
            for pattern, repl in self._patterns:
                msg = pattern.sub(repl, msg)
        return msg


def setup_logging(service_name: Optional[str] = None, cloud: Optional[bool] = None):
    """
    Sets up centralized logging configuration for local and cloud environments.

    This function automatically detects the runtime environment and configures
    the appropriate logging handlers. In GCP environments, it integrates with
    Cloud Logging for centralized log aggregation. In local environments,
    it provides structured console logging.

    Args:
        service_name (Optional[str]): Name of the service for log identification.
            Used for filtering and organizing logs in monitoring systems.
        cloud (Optional[bool]): Force cloud or local mode. If None, auto-detects
            based on GOOGLE_CLOUD_PROJECT environment variable.

    Environment Detection:
        - Cloud mode: GOOGLE_CLOUD_PROJECT environment variable is set
        - Local mode: No GOOGLE_CLOUD_PROJECT detected

    Cloud Configuration:
        - Integrates with Google Cloud Logging API
        - Automatically adds metadata (project, service, version)
        - Supports structured JSON logging

    Local Configuration:
        - Console-based logging with timestamps
        - Human-readable format for development
        - Service name identification

    Example Usage:
        # Basic setup
        setup_logging(service_name="my_agent")

        # Force local mode for testing
        setup_logging(service_name="test_agent", cloud=False)

    For MCP Integration:
        This function ensures consistent logging patterns across all agents,
        enabling proper audit trails and debugging capabilities for agentic workflows.
    """
    # Detect environment
    if cloud is None:
        cloud = bool(os.getenv("GOOGLE_CLOUD_PROJECT"))

    # Debug environment detection
    if cloud:
        logging.debug("Cloud environment detected (GOOGLE_CLOUD_PROJECT set)")
    else:
        logging.debug("Local environment detected (no GOOGLE_CLOUD_PROJECT)")

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Add redacting filter
    redaction_patterns = [
        r"'tomorrow_io_api_key': '[^']+'",
        r"\"apikey\": \"[^\"]+\"",
    ]
    logger.addFilter(RedactingFilter(patterns=redaction_patterns))

    # Remove default handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)

    if cloud:
        try:
            import google.cloud.logging

            client = google.cloud.logging.Client()
            client.setup_logging()
            logging.info("Cloud Logging handler attached successfully")
        except ImportError:
            logging.basicConfig(
                format="%(asctime)s %(levelname)s %(name)s %(message)s",
                level=logging.INFO,
            )
            logging.warning("google-cloud-logging not installed, using basic logging.")
    else:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
            level=logging.INFO,
        )
        logging.info("Local console logging configured")
        if service_name:
            logging.info(f"Service: {service_name}")

    logging.info("Logging setup completed for service: %s", service_name or "unknown")
