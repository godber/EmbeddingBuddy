from dash import html, dcc
import dash_bootstrap_components as dbc


class AboutComponent:
    def _get_about_content(self):
        return """
# 🔍 Interactive Embedding Visualization

EmbeddingBuddy is a modular Python Dash web application for interactive exploration and visualization of embedding vectors through dimensionality reduction techniques (PCA, t-SNE, UMAP).

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
                    dbc.ModalTitle("About EmbeddingBuddy"),
                    close_button=True,
                ),
                dbc.ModalBody([
                    dcc.Markdown(
                        self._get_about_content(),
                        className="mb-0"
                    )
                ]),
                dbc.ModalFooter([
                    dbc.Button(
                        "Close",
                        id="about-modal-close",
                        color="secondary",
                        n_clicks=0
                    )
                ]),
            ],
            id="about-modal",
            is_open=False,
            size="lg",
        )

    def create_about_button(self):
        return dbc.Button(
            [html.I(className="fas fa-info-circle me-2"), "About"],
            id="about-button",
            color="outline-info",
            size="sm",
            n_clicks=0,
            className="ms-2"
        )