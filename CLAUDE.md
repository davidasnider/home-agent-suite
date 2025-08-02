# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a monorepo for a multi-agent home intelligence system built with Google ADK (Agent Development Kit). The system uses a hierarchical agent architecture where specialized agents handle specific tasks like weather planning and home automation.

### Repository Structure
- `agents/` - Individual deployable AI agents, each with their own `pyproject.toml`
- `libs/` - Shared Python libraries used across agents
- Root `pyproject.toml` - Shared development tools (black, flake8, pre-commit)

### Key Design Patterns
- **Monorepo with Poetry**: Uses path dependencies between agents and libraries for local development
- **Shared Logging**: All components use `common_logging.logging_utils.setup_logging()` for consistent logging
- **Tool-based Architecture**: Agents use custom tools to interact with external APIs (Tomorrow.io weather, Home Assistant)
- **Hierarchical Agents**: A supervisor agent delegates tasks to specialized sub-agents

## Development Commands

### Core Commands
```bash
# Install dependencies (run from repo root)
poetry install

# Run tests across all components
poetry run pytest

# Format code
poetry run black .

# Lint code
poetry run flake8 .

# Run pre-commit hooks
pre-commit run --all-files
```

### Infrastructure Management
```bash
# GitHub repository settings (branch protection, etc.)
cd infrastructure/github
poetry install
pulumi stack init dev  # First time only
pulumi config set github:owner davidasnider
pulumi config set --secret github:token YOUR_GITHUB_TOKEN
pulumi up
```

### Per-Agent Development
```bash
# Work on specific agent (e.g., day_planner)
cd agents/day_planner
poetry install  # Install agent-specific dependencies
poetry run pytest  # Run agent tests

# Work on specific library (e.g., tomorrow_io_client)
cd libs/tomorrow_io_client
poetry install
poetry run pytest
```

### Running Weather Client Directly
```bash
# Test Tomorrow.io integration
cd libs/tomorrow_io_client/src
python -m tomorrow_io_client.client
```

## Key Components

### Agents
- **Day Planner Agent** (`agents/day_planner/`) - Provides daily planning advice based on weather forecasts
- **Google Search Agent** (`agents/google_search_agent/`) - Handles web search queries

### Shared Libraries
- **Tomorrow.io Client** (`libs/tomorrow_io_client/`) - Weather API integration with structured response format
- **Common Logging** (`libs/common_logging/`) - Unified logging setup for local and GCP environments

## Code Conventions

### Dependency Management
**CRITICAL**: Always use Poetry for all dependency management across the entire project:
- ✅ **Use Poetry**: All components use `pyproject.toml` with Poetry
- ❌ **Never use pip/requirements.txt**: Inconsistent with project standards
- ✅ **Path dependencies**: Use local path dependencies for monorepo components
- ✅ **Separate pyproject.toml**: Each agent/library/infrastructure component has its own

Examples:
```bash
# Correct: Add new dependency with Poetry
poetry add requests

# Correct: Add development dependency
poetry add --group dev pytest

# Wrong: Never use pip or requirements.txt
pip install requests  # ❌ DON'T DO THIS
```

### Logging Setup
All agents and tools must initialize logging using the shared utility:
```python
from common_logging.logging_utils import setup_logging
setup_logging(service_name="your_agent_name")
```

### Environment Configuration
- Local development uses `.env` files (excluded from git)
- Production uses GCP Secret Manager
- Settings loaded via `pydantic-settings` with `BaseSettings`

### Testing
- Uses pytest with custom pythonpath configuration (see `pytest.ini`)
- Test files follow pattern `test_*.py`
- Mock external API calls using `requests-mock`

## Important Implementation Details

### Tomorrow.io Tool Response Format
The weather tool returns structured dictionaries with this format:
```python
{
    "status": "success|error",
    "forecast": "Human-readable weather summary",
    "location": "Queried location",
    "error_message": "Present if status is error"
}
```

### Path Dependencies
Agents use local path dependencies for development:
```toml
tomorrow-io-client = { path = "../../libs/tomorrow_io_client", develop = true }
```

### Google ADK Integration
- Agents are built as `LlmAgent` instances with custom tools
- Tools follow ADK patterns for function definition and execution
- Agent instructions are defined in code, not separate files

## Testing and Quality
- Pre-commit hooks enforce formatting (black) and linting (flake8)
- Secret detection via `detect-secrets`
- All components should have unit tests
- Mock external API calls in tests
