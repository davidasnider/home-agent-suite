# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set the working directory in the container
WORKDIR /app

# Copy root project files
COPY pyproject.toml README.md ./

# Copy all components (agents and libs)
COPY agents/ agents/
COPY libs/ libs/
COPY ui/ ui/
COPY app.py ./

# Install dependencies from the root pyproject.toml
# This will also install the local path dependencies for agents/libs
RUN poetry install --no-interaction --no-ansi --no-root

# Install dependencies for all components to ensure they are available
RUN for dir in agents/* libs/*; do \
        if [ -f "$dir/pyproject.toml" ]; then \
            echo "Installing dependencies for $dir"; \
            (cd "$dir" && poetry install --no-interaction --no-ansi); \
        fi \
    done

# Expose the port Streamlit runs on
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Command to run the application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
