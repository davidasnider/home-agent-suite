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

## Development Workflow

### Starting Any Development Session
**CRITICAL**: Always follow this workflow when starting work:

**If starting from main branch:**
1. **Pull latest changes**: `git pull origin main`
2. **Run tests**: `poetry run pytest` to ensure everything works
3. **Create feature branch**: `git checkout -b descriptive-branch-name`

**If on an existing feature branch:**
1. **Run tests**: `poetry run pytest` to ensure everything works
2. **Continue on current branch** (no need to create new branch)

This ensures you're working with the latest code and all tests pass before making changes.

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

## Todo Management
**IMPORTANT**: Use GitHub Issues exclusively for todo tracking and task management.

- When asked to record a todo, create a GitHub Issue with appropriate labels and details
- Include relevant code references, file paths, and context in issue descriptions
- Use labels to categorize: `bug`, `enhancement`, `documentation`, `technical-debt`, etc.
- Link related issues and PRs when relevant
- Close issues when tasks are completed

**Never use**: Markdown files, local notes, or other todo systems - GitHub Issues only.

### Code Style and Linting Standards
**CRITICAL**: Always write code that follows these standards from the start to avoid extensive cleanup:

#### Flake8 Rules (Max Line Length: 88 characters)
- **Line length**: Keep lines under 88 characters, break at ~85 to be safe
- **Remove unused imports**: Delete any imports that aren't actually used in the code
- **Exception handling**: Never use bare `except:` - always specify `Exception` or specific exception types
- **F-string usage**: Don't use f-strings without placeholders - use regular strings instead
- **Import organization**: Group imports properly (standard library, third-party, local)

#### Black Formatting
- **Multi-line strings**: Use parentheses for long strings instead of single long lines:
  ```python
  # Good
  message = (
      "This is a long message that spans multiple lines "
      "and stays within the line length limit"
  )

  # Bad
  message = "This is a long message that spans multiple lines and goes over the line length limit"
  ```
- **Function calls**: Break long function calls across multiple lines with proper indentation
- **String concatenation**: Use parentheses for readability instead of backslash line continuation

#### Common Patterns to Avoid
```python
# Bad - unused imports
from typing import Dict, List, Any, Optional  # Remove if not used
import os  # Remove if not used

# Bad - bare except
try:
    do_something()
except:  # Should be 'except Exception:'
    handle_error()

# Bad - f-string without placeholder
logger.debug(f"Starting process")  # Should be regular string

# Bad - line too long
logger.debug("This is a very long debug message that exceeds the 88 character limit and will cause flake8 errors")

# Good - proper formatting
logger.debug(
    "This is a long debug message that is properly formatted "
    "to stay within line length limits"
)
```

- add to memory. Always use pre-commit on all files for linting and formatting. Do not run those commands directly
