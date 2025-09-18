from dash import html, dcc
import dash_bootstrap_components as dbc


class AboutComponent:
    def _get_about_content(self):
        return """
# 🔍 Interactive Embedding Vector Visualization

EmbeddingBuddy is a web application for interactive exploration and
visualization of embedding vectors through dimensionality reduction techniques
(PCA, t-SNE, UMAP).

You have two ways to get started:

1. Generate embeddings directly in the browser if it supports WebGPU.
2. Upload your NDJSON file containing embedding vectors and metadata.

## Generating Embeddings in Browser

1. Expand the "Generate Embeddings" section.
2. Input your text data (one entry per line).
    1. Optionally you can use the built in sample data by clicking "Load Sample Data" button.
3. Click "Generate Embeddings" to create vectors using a pre-trained model.

## NDJSON File Format

```json
{"id": "doc_001", "embedding": [0.1, -0.3, 0.7, ...], "text": "Sample text content", "category": "news", "subcategory": "politics", "tags": ["election", "politics"]}
{"id": "doc_002", "embedding": [0.2, -0.1, 0.9, ...], "text": "Another example", "category": "review", "subcategory": "product", "tags": ["tech", "gadget"]}
```


## ✨ Features

- Drag-and-drop NDJSON file upload
- Multiple dimensionality reduction algorithms
- 2D/3D interactive plots with Plotly
- Color coding by categories, subcategories, or tags
- In-browser embedding generation
- OpenSearch integration for data loading

## 🔧 Supported Algorithms

- **PCA** (Principal Component Analysis)
- **t-SNE** (t-Distributed Stochastic Neighbor Embedding)
- **UMAP** (Uniform Manifold Approximation and Projection)

---

📂 [View on GitHub](https://github.com/godber/EmbeddingBuddy)

*Built with: Python, Dash, Plotly, scikit-learn, OpenTSNE, UMAP*
        """.strip()

    def create_about_modal(self):
        return dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("Welcome to EmbeddingBuddy"),
                    close_button=True,
                ),
                dbc.ModalBody(
                    [dcc.Markdown(self._get_about_content(), className="mb-0")]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            "Close",
                            id="about-modal-close",
                            color="secondary",
                            n_clicks=0,
                        )
                    ]
                ),
            ],
            id="about-modal",
            is_open=True,
            size="lg",
        )

    def create_about_button(self):
        return dbc.Button(
            [html.I(className="fas fa-info-circle me-2"), "About"],
            id="about-button",
            color="outline-info",
            size="sm",
            n_clicks=0,
            className="ms-2",
        )
