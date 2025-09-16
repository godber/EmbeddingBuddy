import dash
import dash_bootstrap_components as dbc
from .config.settings import AppSettings
from .ui.layout import AppLayout
from .ui.callbacks.data_processing import DataProcessingCallbacks
from .ui.callbacks.visualization import VisualizationCallbacks
from .ui.callbacks.interactions import InteractionCallbacks


def create_app():
    import os

    # Get the project root directory (two levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    assets_path = os.path.join(project_root, "assets")

    app = dash.Dash(
        __name__,
        title="EmbeddingBuddy",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        ],
        assets_folder=assets_path,
        meta_tags=[
            {
                "name": "description",
                "content": "Interactive embedding visualization tool for exploring high-dimensional vectors through dimensionality reduction techniques like PCA, t-SNE, and UMAP.",
            },
            {"name": "author", "content": "EmbeddingBuddy"},
            {
                "name": "keywords",
                "content": "embeddings, visualization, dimensionality reduction, PCA, t-SNE, UMAP, machine learning, data science",
            },
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
            {
                "property": "og:title",
                "content": "EmbeddingBuddy - Interactive Embedding Visualization",
            },
            {
                "property": "og:description",
                "content": "Explore and visualize embedding vectors through interactive 2D/3D plots with multiple dimensionality reduction techniques.",
            },
            {"property": "og:type", "content": "website"},
        ],
    )

    # Allow callbacks to components that are dynamically created in tabs
    app.config.suppress_callback_exceptions = True

    layout_manager = AppLayout()
    app.layout = layout_manager.create_layout()

    DataProcessingCallbacks()
    VisualizationCallbacks()
    InteractionCallbacks()

    # Register client-side callback for embedding generation
    _register_client_side_callbacks(app)

    return app


def _register_client_side_callbacks(app):
    """Register client-side callbacks for browser-based processing."""
    from dash import Input, Output, State

    # Client-side callback for embedding generation
    app.clientside_callback(
        """
        function(nClicks, textContent, modelName, tokenizationMethod, batchSize, category, subcategory) {
            if (!nClicks || !textContent || !textContent.trim()) {
                return window.dash_clientside.no_update;
            }

            console.log('🔍 Checking for Transformers.js...');
            console.log('window.dash_clientside:', typeof window.dash_clientside);
            console.log('window.dash_clientside.transformers:', typeof window.dash_clientside?.transformers);
            console.log('generateEmbeddings function:', typeof window.dash_clientside?.transformers?.generateEmbeddings);

            if (typeof window.dash_clientside !== 'undefined' &&
                typeof window.dash_clientside.transformers !== 'undefined' &&
                typeof window.dash_clientside.transformers.generateEmbeddings === 'function') {

                console.log('✅ Calling Transformers.js generateEmbeddings...');
                return window.dash_clientside.transformers.generateEmbeddings(
                    nClicks, textContent, modelName, tokenizationMethod, category, subcategory
                );
            }

            // More detailed error information
            let errorMsg = '❌ Transformers.js not available. ';
            if (typeof window.dash_clientside === 'undefined') {
                errorMsg += 'dash_clientside not found.';
            } else if (typeof window.dash_clientside.transformers === 'undefined') {
                errorMsg += 'transformers module not found.';
            } else if (typeof window.dash_clientside.transformers.generateEmbeddings !== 'function') {
                errorMsg += 'generateEmbeddings function not found.';
            }

            console.error(errorMsg);

            return [
                { error: 'Transformers.js not loaded. Please refresh the page and try again.' },
                false
            ];
        }
        """,
        [
            Output("embeddings-generated-trigger", "data"),
            Output("generate-embeddings-btn", "disabled", allow_duplicate=True),
        ],
        [Input("generate-embeddings-btn", "n_clicks")],
        [
            State("text-input-area", "value"),
            State("model-selection", "value"),
            State("tokenization-method", "value"),
            State("batch-size", "value"),
            State("text-category", "value"),
            State("text-subcategory", "value"),
        ],
        prevent_initial_call=True,
    )


def run_app(app=None, debug=None, host=None, port=None):
    if app is None:
        app = create_app()

    app.run(
        debug=debug if debug is not None else AppSettings.DEBUG,
        host=host if host is not None else AppSettings.HOST,
        port=port if port is not None else AppSettings.PORT,
    )


if __name__ == "__main__":
    app = create_app()
    run_app(app)
