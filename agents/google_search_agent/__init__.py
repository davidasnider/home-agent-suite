"""
Google Search Agent Package

This package provides an intelligent research agent that leverages Google Search
to deliver accurate, fact-based answers and comprehensive research capabilities.

The agent specializes in real-time information retrieval, going beyond training data
to provide current, verified information from authoritative web sources.

Main Components:
- agent.py: Agent configuration with Google Search integration

Key Capabilities:
- Real-time web search and information retrieval
- Fact verification and source attribution
- Multi-step research workflows
- Current events and breaking news analysis

Usage:
    from agents.google_search_agent import root_agent
    # Agent ready for research and fact-checking queries

For MCP Integration:
This agent maintains search result traceability and provides source attribution,
making it ideal for composable research workflows and fact-checking pipelines.
"""

from . import agent  # noqa: F401
