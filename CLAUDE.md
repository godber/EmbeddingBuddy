# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

EmbeddingBuddy is a modular Python Dash web application for interactive exploration and
visualization of embedding vectors through dimensionality reduction techniques
(PCA, t-SNE, UMAP). The app provides a drag-and-drop interface for uploading
NDJSON files containing embeddings and visualizes them in 2D/3D plots. The codebase
follows a clean, modular architecture that prioritizes testability and maintainability.

## Development Commands

**Install dependencies:**

```bash
uv sync
```

**Run the application:**

Development mode (with auto-reload):
```bash
uv run run_dev.py
```

Production mode (with Gunicorn WSGI server):
```bash
# First install production dependencies
uv sync --extra prod

# Then run in production mode
uv run run_prod.py
```

Legacy mode (basic Dash server):
```bash
uv run main.py
```

The app will be available at http://127.0.0.1:8050

**Run tests:**

```bash
uv sync --extra test
uv run pytest tests/ -v
```

**Development tools:**

```bash
# Install all dev dependencies
uv sync --extra dev

# Linting and formatting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type checking
uv run mypy src/embeddingbuddy/

# Security scanning
uv run bandit -r src/
uv run safety check
```

**Test with sample data:**
Use the included `sample_data.ndjson` and `sample_prompts.ndjson` files for testing the application functionality.

## Architecture

### Project Structure

The application follows a modular architecture with clear separation of concerns:

```text
src/embeddingbuddy/
├── app.py              # Main application entry point and factory
├── main.py             # Application runner
├── config/
│   └── settings.py     # Centralized configuration management
├── data/
│   ├── parser.py       # NDJSON parsing logic
│   └── processor.py    # Data transformation and processing
├── models/
│   ├── schemas.py      # Data models and validation schemas
│   └── reducers.py     # Dimensionality reduction algorithms
├── visualization/
│   ├── plots.py        # Plot creation and factory classes
│   └── colors.py       # Color mapping and management
├── ui/
│   ├── layout.py       # Main application layout
│   ├── components/     # Reusable UI components
│   │   ├── sidebar.py  # Sidebar component
│   │   └── upload.py   # Upload components
│   └── callbacks/      # Organized callback functions
│       ├── data_processing.py  # Data upload/processing callbacks
│       ├── visualization.py    # Plot update callbacks
│       └── interactions.py     # User interaction callbacks
└── utils/              # Utility functions and helpers
```

### Key Components

**Data Layer:**

- `data/parser.py` - NDJSON parsing with error handling
- `data/processor.py` - Data transformation and combination logic
- `models/schemas.py` - Dataclasses for type safety and validation

**Algorithm Layer:**

- `models/reducers.py` - Modular dimensionality reduction with factory pattern
- Supports PCA, t-SNE (openTSNE), and UMAP algorithms
- Abstract base class for easy extension

**Visualization Layer:**

- `visualization/plots.py` - Plot factory with single and dual plot support
- `visualization/colors.py` - Color mapping and grayscale conversion utilities
- Plotly-based 2D/3D scatter plots with interactive features

**UI Layer:**

- `ui/layout.py` - Main application layout composition
- `ui/components/` - Reusable, testable UI components
- `ui/callbacks/` - Organized callbacks grouped by functionality
- Bootstrap-styled sidebar with controls and large visualization area

**Configuration:**

- `config/settings.py` - Centralized settings with environment variable support
- Plot styling, marker configurations, and app-wide constants

### Data Format

The application expects NDJSON files where each line contains:

```json
{"id": "doc_001", "embedding": [0.1, -0.3, 0.7, ...], "text": "Sample text", "category": "news", "subcategory": "politics", "tags": ["election"]}
```

Required fields: `embedding` (array), `text` (string)
Optional fields: `id`, `category`, `subcategory`, `tags`

### Callback Architecture

The refactored callback system is organized by functionality:

**Data Processing (`ui/callbacks/data_processing.py`):**

- File upload handling
- NDJSON parsing and validation
- Data storage in dcc.Store components

**Visualization (`ui/callbacks/visualization.py`):**

- Dimensionality reduction pipeline
- Plot generation and updates
- Method/parameter change handling

**Interactions (`ui/callbacks/interactions.py`):**

- Point click handling and detail display
- Reset functionality
- User interaction management

### Testing Architecture

The modular design enables comprehensive testing:

**Unit Tests:**

- `tests/test_data_processing.py` - Parser and processor logic
- `tests/test_reducers.py` - Dimensionality reduction algorithms
- `tests/test_visualization.py` - Plot creation and color mapping

**Integration Tests:**

- End-to-end data pipeline testing
- Component integration verification

**Key Testing Benefits:**

- Fast test execution (milliseconds vs seconds)
- Isolated component testing
- Easy mocking and fixture creation
- High code coverage achievable

## Dependencies

Uses modern Python stack with uv for dependency management:

- **Core Framework:** Dash + Plotly for web interface and visualization
- **Algorithms:** scikit-learn (PCA), openTSNE, umap-learn for dimensionality reduction
- **Data:** pandas/numpy for data manipulation
- **UI:** dash-bootstrap-components for styling
- **Testing:** pytest for test framework
- **Dev Tools:** uv for package management

## Development Guidelines

**When adding new features:**

1. **Data Models** - Add/update schemas in `models/schemas.py`
2. **Algorithms** - Extend `models/reducers.py` using the abstract base class
3. **UI Components** - Create reusable components in `ui/components/`
4. **Configuration** - Add settings to `config/settings.py`
5. **Tests** - Write tests for all new functionality

**Code Organization Principles:**

- Single responsibility principle
- Clear module boundaries  
- Testable, isolated components
- Configuration over hardcoding
- Error handling at appropriate layers

**Testing Requirements:**

- Unit tests for all core logic
- Integration tests for data flow
- Component tests for UI elements
- Maintain high test coverage
