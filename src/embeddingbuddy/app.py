"""
EmbeddingBuddy application factory and server functions.

This module contains the main application creation logic with imports
moved inside functions to avoid loading heavy dependencies at module level.
"""


def create_app():
    """Create and configure the Dash application instance."""
    import os
    import dash
    import dash_bootstrap_components as dbc
    from .ui.layout import AppLayout
    from .ui.callbacks.data_processing import DataProcessingCallbacks
    from .ui.callbacks.visualization import VisualizationCallbacks
    from .ui.callbacks.interactions import InteractionCallbacks

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
    """Run the Dash application with specified settings."""
    from .config.settings import AppSettings

    if app is None:
        app = create_app()

    app.run(
        debug=debug if debug is not None else AppSettings.DEBUG,
        host=host if host is not None else AppSettings.HOST,
        port=port if port is not None else AppSettings.PORT,
    )


def serve(host=None, port=None, dev=False, debug=False):
    """Start the EmbeddingBuddy web server.

    Args:
        host: Host to bind to (default: 127.0.0.1)
        port: Port to bind to (default: 8050)
        dev: Development mode - enable debug logging and auto-reload (default: False)
        debug: Enable debug logging only, no auto-reload (default: False)
    """
    import os
    from .config.settings import AppSettings

    # Determine actual values to use
    actual_host = host if host is not None else AppSettings.HOST
    actual_port = port if port is not None else AppSettings.PORT

    # Determine mode
    # --dev takes precedence and enables both debug and auto-reload
    # --debug enables only debug logging
    # No flags = production mode (no debug, no auto-reload)
    use_reloader = dev
    use_debug = dev or debug

    # Only print startup messages in main process (not in Flask reloader)
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        mode = "development" if dev else ("debug" if debug else "production")
        print(f"Starting EmbeddingBuddy in {mode} mode...")
        print("Loading dependencies (this may take a few seconds)...")
        print(f"Server will start at http://{actual_host}:{actual_port}")
        if use_reloader:
            print("Auto-reload enabled - server will restart on code changes")

    app = create_app()

    # Suppress Flask development server warning in production mode
    if not use_debug and not use_reloader:
        import warnings
        import logging

        # Suppress the werkzeug warning
        warnings.filterwarnings("ignore", message=".*development server.*")

        # Set werkzeug logger to ERROR level to suppress the warning
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.ERROR)

    # Use Flask's built-in server with appropriate settings
    app.run(
        debug=use_debug, host=actual_host, port=actual_port, use_reloader=use_reloader
    )


def main():
    """Legacy entry point - redirects to cli module.

    This is kept for backward compatibility but the main CLI
    is now in embeddingbuddy.cli for faster startup.
    """
    from .cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
