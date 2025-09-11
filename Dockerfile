FROM python:3.12-slim-bullseye AS builder

# Build arguments
ARG APP_DIR=/app
ARG UID=1000
ARG GID=1000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR ${APP_DIR}

# Copy project files
COPY pyproject.toml .

# Install dependencies with uv
RUN uv sync

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -g ${GID} appuser && useradd -u ${UID} -g ${GID} -s /bin/bash appuser
RUN chown -R appuser:appuser ${APP_DIR}

# Runtime stage
FROM builder AS runtime

# Switch to non-root user
USER appuser

# Add virtual environment to PATH
ENV PATH="${APP_DIR}/.venv/bin:$PATH"

CMD ["python", "-m", "app"]
