# Two-stage Dockerfile for EmbeddingBuddy
# Stage 1: Builder
FROM python:3.11-slim as builder

# Create non-root user early in builder stage
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy source code (needed for editable install)
COPY src/ src/
COPY assets/ assets/

# Change ownership of source files before building (lighter I/O)
RUN chown -R appuser:appuser /app

# Create and set permissions for appuser home directory (needed for uv cache)
RUN mkdir -p /home/appuser && chown -R appuser:appuser /home/appuser

# Switch to non-root user before building
USER appuser

# Create virtual environment and install dependencies (including production extras)
RUN uv venv .venv
RUN uv sync --frozen --extra prod 

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Create non-root user in runtime stage
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies for compiled packages
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory and change ownership (small directory)
WORKDIR /app
RUN chown appuser:appuser /app

# Copy files from builder with correct ownership
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/src /app/src
COPY --from=builder --chown=appuser:appuser /app/assets /app/assets

# Switch to non-root user
USER appuser

# Make sure the virtual environment is in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Set Python path
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Environment variables for production
ENV EMBEDDINGBUDDY_HOST=0.0.0.0
ENV EMBEDDINGBUDDY_PORT=8050
ENV EMBEDDINGBUDDY_DEBUG=false
ENV EMBEDDINGBUDDY_ENV=production

# Expose port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8050/', timeout=5)" || exit 1

# Run application in production mode (no debug, no auto-reload)
CMD ["embeddingbuddy", "serve"]