# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

EmbeddingBuddy is a Python Dash web application for interactive exploration and
visualization of embedding vectors through dimensionality reduction techniques
(PCA, t-SNE, UMAP). The app provides a drag-and-drop interface for uploading
NDJSON files containing embeddings and visualizes them in 2D/3D plots.

## Development Commands

**Install dependencies:**

```bash
uv sync
```

**Run the application:**

```bash
uv run python app.py
```

The app will be available at http://127.0.0.1:8050

**Test with sample data:**
Use the included `sample_data.ndjson` file for testing the application functionality.

## Architecture

### Core Files

- `app.py` - Main Dash application with complete web interface, data processing,
   and visualization logic
- `main.py` - Simple entry point (currently minimal)
- `pyproject.toml` - Project configuration and dependencies using uv package manager

### Key Components

- **Data Processing**: NDJSON parser that handles embedding documents with
  required fields (`embedding`, `text`) and optional metadata (`id`, `category`, `subcategory`, `tags`)
- **Dimensionality Reduction**: Supports PCA, t-SNE (openTSNE), and UMAP algorithms
- **Visualization**: Plotly-based 2D/3D scatter plots with interactive features
- **UI Layout**: Bootstrap-styled sidebar with controls and large visualization area
- **State Management**: Dash callbacks for reactive updates between upload,
  method selection, and plot rendering

### Data Format

The application expects NDJSON files where each line contains:

```json
{"id": "doc_001", "embedding": [0.1, -0.3, 0.7, ...], "text": "Sample text", "category": "news", "subcategory": "politics", "tags": ["election"]}
```

### Callback Architecture

- File upload → Data processing and storage in dcc.Store
- Method/parameter changes → Dimensionality reduction and plot update
- Point clicks → Detail display in sidebar

## Dependencies

Uses modern Python stack with uv for dependency management:

- Dash + Plotly for web interface and visualization
- scikit-learn (PCA), openTSNE, umap-learn for dimensionality reduction
- pandas/numpy for data manipulation
- dash-bootstrap-components for styling