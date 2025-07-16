# Project Agent and Tool Manifest

This document provides high-level context for the AI agents and tools within the `home-agent-suite` project. It is intended to ground GitHub CoPilot and assist human developers in understanding the system's architecture.

## Repository Structure

  - `/agents`: Contains individual, deployable AI agents built with Google ADK. Each agent has its own `pyproject.toml`.
  - `/libs`: Contains shared Python libraries used by agents. These are designed to be reusable across the system.

-----

## Core Agents

### 1\. SupervisorAgent

  - **Location:** `agents/supervisor/`
  - **Purpose:** Acts as the central coordinator. It receives all user requests and delegates them to the appropriate specialist sub-agent.
  - **Type:** `google.adk.agents.LlmAgent`
  - **Key Logic:** Uses LLM-driven routing based on the descriptions of its sub-agents to determine the correct expert for a task.
  - **Core Instructions:** For the definitive prompt, see the `instruction` parameter in `agents/supervisor/src/supervisor/agent.py`.

### 2\. DayPlannerAgent

  - **Location:** `agents/day_planner/`
  - **Purpose:** Provides daily planning advice to the user based on a detailed weather forecast.
  - **Type:** `google.adk.agents.LlmAgent` (Sub-agent to SupervisorAgent)
  - **Key Logic:** Analyzes an hourly weather forecast to identify the most pleasant time window for outdoor activities.
  - **Core Instructions:** For the definitive prompt, see the `instruction` parameter in `agents/day_planner/src/day_planner/agent.py`.

### 3\. HomeAssistantAgent

  - **Location:** `agents/home_assistant_agent/`
  - **Purpose:** Monitors and controls smart devices connected to a Home Assistant instance.
  - **Type:** `google.adk.agents.LlmAgent` (Sub-agent to SupervisorAgent)
  - **Key Logic:** Interprets user commands to query device states or call services within Home Assistant.
  - **Core Instructions:** For the definitive prompt, see the `instruction` parameter in `agents/home_assistant_agent/src/home_assistant_agent/agent.py`.

-----

## Core Tools

### 1\. TomorrowIoTool

  - **Location:** `libs/tomorrow_io_client/`
  - **Purpose:** An ADK-compatible tool for fetching and summarizing weather forecasts from the Tomorrow.io API.
  - **Functionality:**
      - Calls the Tomorrow.io `/v4/weather/forecast` endpoint.
      - Accepts a `location` string (e.g., "New York, NY" or "zip:10001") as input.
      - Processes the raw hourly JSON response and returns a simplified, human-readable summary of the day's weather, broken down into morning, afternoon, and evening segments. This summary is designed to be easily parsed by an LLM.

### 2\. HomeAssistantTool

  - **Location:** `libs/home_assistant_client/`
  - **Purpose:** An ADK-compatible tool for interacting with the Home Assistant REST API.
  - **Functionality:**
      - Authenticates using a Long-Lived Access Token.
      - Exposes a `get_state` function to retrieve the status and attributes of any entity.
      - Exposes a `call_service` function to execute actions on entities (e.g., `light.turn_on`, `cover.open_cover`).
