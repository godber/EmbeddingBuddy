# EmbeddingBuddy

A modular Python Dash web application for interactive exploration and visualization of embedding
vectors through dimensionality reduction techniques. Compare documents and prompts
in the same embedding space to understand semantic relationships.

![Screenshot of 3d graph and UI for Embedding Buddy](./embedding-buddy-screenshot.png)

## Overview

EmbeddingBuddy provides an intuitive web interface for analyzing high-dimensional
embedding vectors by applying various dimensionality reduction algorithms and
visualizing the results in interactive 2D and 3D plots. The application features
a clean, modular architecture that makes it easy to test, maintain, and extend
with new features. It supports dual dataset visualization, allowing you to compare
documents and prompts to understand how queries relate to your content.

## Features

- **Dual file upload** - separate drag-and-drop for documents and prompts
- **Multiple dimensionality reduction methods**: PCA, t-SNE, and UMAP
- **Interactive 2D/3D visualizations** with toggle between views
- **Color coding options** by category, subcategory, or tags
- **Visual distinction**: Documents appear as circles, prompts as diamonds with desaturated colors
- **Prompt visibility toggle** - show/hide prompts to reduce visual clutter
- **Point inspection** - click points to view full content and identify document vs prompt
- **Reset functionality** - clear all data to start fresh
- **Sidebar layout** with controls on left, large visualization area on right
- **Real-time visualization** optimized for small to medium datasets

## Quick Start

### Installation

**Option 1: Install with uv (recommended)**

```bash
# Install as a CLI tool (no need to clone the repo)
uv tool install embeddingbuddy

# Run the application
embeddingbuddy serve
```

**Option 2: Install with pip/pipx**

```bash
# Install with pipx (isolated environment)
pipx install embeddingbuddy

# Or install with pip
pip install embeddingbuddy

# Run the application
embeddingbuddy
```

**Option 3: Run with Docker**

```bash
# Pull and run the Docker image
docker run -p 8050:8050 ghcr.io/godber/embedding-buddy:latest
```

The application will be available at <http://127.0.0.1:8050>

### Using the Application

1. **Open your browser** to <http://127.0.0.1:8050>
2. **Upload your data**:
   - Drag and drop an NDJSON file containing embeddings (see Data Format below)
   - Optionally upload a second file with prompts to compare against documents
3. **Choose visualization settings**:
   - Select dimensionality reduction method (PCA, t-SNE, or UMAP)
   - Choose 2D or 3D visualization
   - Pick color coding (by category, subcategory, or tags)
4. **Explore**:
   - Click points to view full content
   - Toggle prompt visibility
   - Rotate and zoom 3D plots

## Data Format

EmbeddingBuddy accepts newline-delimited JSON (NDJSON) files for both documents
and prompts. Each line contains an embedding with the following structure:

**Documents:**

```json
{"id": "doc_001", "embedding": [0.1, -0.3, 0.7, ...], "text": "Sample text content", "category": "news", "subcategory": "politics", "tags": ["election", "politics"]}
{"id": "doc_002", "embedding": [0.2, -0.1, 0.9, ...], "text": "Another example", "category": "review", "subcategory": "product", "tags": ["tech", "gadget"]}
```

**Prompts:**

```json
{"id": "prompt_001", "embedding": [0.15, -0.28, 0.65, ...], "text": "Find articles about machine learning applications", "category": "search", "subcategory": "technology", "tags": ["AI", "research"]}
{"id": "prompt_002", "embedding": [0.72, 0.18, -0.35, ...], "text": "Show me product reviews for smartphones", "category": "search", "subcategory": "product", "tags": ["mobile", "reviews"]}
```

**Required Fields:**

- `embedding`: Array of floating-point numbers representing the vector (must be same dimensionality for both documents and prompts)
- `text`: String content associated with the embedding

**Optional Fields:**

- `id`: Unique identifier (auto-generated if missing)
- `category`: Primary classification
- `subcategory`: Secondary classification
- `tags`: Array of string tags for flexible labeling

**Important:** Document and prompt embeddings must have the same number of dimensions to be visualized together.

## Installation & Usage

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

1. **Install dependencies:**

```bash
uv sync
```

2. **Run the application:**

```bash
# Production mode (no debug, no auto-reload)
embeddingbuddy serve

# Development mode (debug + auto-reload on code changes)
embeddingbuddy serve --dev

# Debug logging only (no auto-reload)
embeddingbuddy serve --debug

# Custom host/port
embeddingbuddy serve --host 0.0.0.0 --port 8080
```

3. **Open your browser** to <http://127.0.0.1:8050>

4. **Test with sample data**:
   - Upload `sample_data.ndjson` (documents)
   - Upload `sample_prompts.ndjson` (prompts) to see dual visualization
   - Use the "Show prompts" toggle to compare how prompts relate to documents

## Docker

You can also run EmbeddingBuddy using Docker:

### Basic Usage

```bash
# Run in the background
docker compose up -d
```

The application will be available at <http://127.0.0.1:8050>

### With OpenSearch

To run with OpenSearch for enhanced search capabilities:

```bash
# Run in the background with OpenSearch
docker compose --profile opensearch up -d
```

This will start both the EmbeddingBuddy application and an OpenSearch instance.
OpenSearch will be available at <http://127.0.0.1:9200>

### Docker Commands

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs embeddingbuddy
docker compose logs opensearch

# Rebuild containers
docker compose build
```

## Development

### Project Structure

The application follows a modular architecture for improved maintainability and testability:

```text
src/embeddingbuddy/
├── app.py                     # Main application entry point and factory
├── config/                    # Configuration management
│   └── settings.py            # Centralized app settings
├── data/                      # Data parsing and processing
│   ├── parser.py              # NDJSON parsing logic
│   ├── processor.py           # Data transformation utilities
│   └── sources/               # Data source integrations
│       └── opensearch.py      # OpenSearch data source
├── models/                    # Data schemas and algorithms
│   ├── schemas.py             # Pydantic data models
│   ├── reducers.py            # Dimensionality reduction algorithms
│   └── field_mapper.py        # Field mapping utilities
├── visualization/             # Plot creation and styling
│   ├── plots.py               # Plot factory and creation logic
│   └── colors.py              # Color mapping utilities
├── ui/                        # User interface components
│   ├── layout.py              # Main application layout
│   ├── components/            # Reusable UI components
│   │   ├── sidebar.py         # Sidebar component
│   │   ├── upload.py          # Upload components
│   │   ├── textinput.py       # Text input components
│   │   └── datasource.py      # Data source components
│   └── callbacks/             # Organized callback functions
│       ├── data_processing.py # Data upload/processing callbacks
│       ├── visualization.py   # Plot update callbacks
│       └── interactions.py    # User interaction callbacks
└── utils/                     # Utility functions

# CLI entry point
embeddingbuddy serve    # Main CLI command to start the server
```

### Testing

Run the test suite to verify functionality:

```bash
# Install test dependencies
uv sync --extra test

# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_data_processing.py -v

# Run with coverage
uv run pytest tests/ --cov=src/embeddingbuddy
```

### Development Tools

Install development dependencies for linting, type checking, and security:

```bash
# Install all dev dependencies
uv sync --extra dev

# Or install specific groups
uv sync --extra test        # Testing tools
uv sync --extra lint        # Linting and formatting
uv sync --extra security    # Security scanning tools

# Run linting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Run type checking
uv run mypy src/embeddingbuddy/

# Run security scans
uv run bandit -r src/
uv run safety check
```

### Adding New Features

The modular architecture makes it easy to extend functionality:

- **New reduction algorithms**: Add to `models/reducers.py`
- **New plot types**: Extend `visualization/plots.py`
- **UI components**: Add to `ui/components/`
- **Configuration options**: Update `config/settings.py`

## Tech Stack

- **Python Dash**: Web application framework
- **Plotly**: Interactive plotting and visualization
- **scikit-learn**: PCA implementation
- **UMAP-learn**: UMAP dimensionality reduction
- **openTSNE**: Fast t-SNE implementation
- **NumPy/Pandas**: Data manipulation and analysis
- **pytest**: Testing framework
- **uv**: Modern Python package and project manager
