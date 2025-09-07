# Two-stage Dockerfile for EmbeddingBuddy
# Stage 1: Builder
FROM python:3.11-slim as builder

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
COPY main.py .
COPY assets/ assets/

# Create virtual environment and install dependencies
RUN uv venv .venv
RUN uv sync --frozen 

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Install runtime dependencies for compiled packages
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application files from builder stage
COPY --from=builder /app/src /app/src
COPY --from=builder /app/main.py /app/main.py
COPY --from=builder /app/assets /app/assets

# Make sure the virtual environment is in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Set Python path
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Environment variables for production
ENV EMBEDDINGBUDDY_HOST=0.0.0.0
ENV EMBEDDINGBUDDY_PORT=8050
ENV EMBEDDINGBUDDY_DEBUG=False

# Expose port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8050/', timeout=5)" || exit 1

# Run application
CMD ["python", "main.py"]