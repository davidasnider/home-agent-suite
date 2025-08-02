"""
Tomorrow.io Weather API Client Package

This package provides a production-ready client for the Tomorrow.io weather API,
designed specifically for integration with AI agents and MCP systems.

The client transforms raw weather data into structured, LLM-friendly summaries
that enable intelligent decision-making in weather-dependent applications.

Key Features:
- Tomorrow.io API v4 integration
- Intelligent weather data summarization
- Error handling and retry logic
- Local timezone awareness
- Production configuration management

Main Components:
- client.py: Core API client and data processing functions
- Settings class: Configuration management with environment variable support

API Capabilities:
- Hourly weather forecasts up to 7 days
- Location-flexible queries (city names, coordinates, zip codes)
- Structured response format optimized for AI consumption

Usage:
    from tomorrow_io_client.client import get_tmrw_weather_tool

    weather_data = get_tmrw_weather_tool("New York, NY")
    # Returns structured weather summary for AI agent consumption

For MCP Integration:
This package provides deterministic, structured weather data that enables
reliable weather-based decision making in agentic workflows.
"""

# Initialize logging for package-level usage
from common_logging.logging_utils import setup_logging

setup_logging(service_name="tomorrow_io_client")
