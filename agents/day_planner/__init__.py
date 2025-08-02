"""
Day Planner Agent Package

This package provides an intelligent day planning agent that combines weather data
with activity recommendations to help users optimize their daily schedules.

The agent leverages real-time weather forecasts from Tomorrow.io to suggest the best
time windows for outdoor activities and provides indoor alternatives when weather
conditions are unfavorable.

Main Components:
- agent.py: Agent configuration and initialization
- prompt.py: Structured instruction prompts for consistent behavior

Usage:
    from agents.day_planner import root_agent
    # Agent ready for weather-based planning queries

For MCP Integration:
This package follows Model Context Protocol patterns for reliable agent interactions
and supports composable workflows with other home automation agents.
"""

from . import agent  # noqa: F401
