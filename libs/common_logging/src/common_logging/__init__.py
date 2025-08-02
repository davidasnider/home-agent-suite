"""
Common Logging Package

This package provides centralized logging utilities for the home-agent-suite system,
ensuring consistent log formatting and handling across all agents and services.

The logging system automatically adapts to different deployment environments:
- Local development: Console logging with human-readable formats
- Google Cloud Platform: Integration with Cloud Logging for centralized monitoring

Key Features:
- Automatic environment detection (local vs cloud)
- Structured logging for better searchability
- Service identification and categorization
- Error handling and fallback mechanisms

Main Components:
- logging_utils.py: Core logging configuration functions

Usage:
    from common_logging.logging_utils import setup_logging
    setup_logging(service_name="my_service")

For MCP and Agentic Systems:
This package enables distributed tracing, audit trails, and debugging capabilities
essential for complex multi-agent workflows and service interactions.
"""
