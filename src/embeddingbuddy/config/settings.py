from typing import Dict, Any
import os


class AppSettings:
    # UI Configuration
    UPLOAD_STYLE = {
        "width": "100%",
        "height": "60px",
        "lineHeight": "60px",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin-bottom": "20px",
    }

    PROMPTS_UPLOAD_STYLE = {**UPLOAD_STYLE, "borderColor": "#28a745"}

    PLOT_CONFIG = {"responsive": True, "displayModeBar": True}

    PLOT_STYLE = {"height": "85vh", "width": "100%"}

    PLOT_LAYOUT_CONFIG = {
        "height": None,
        "autosize": True,
        "margin": dict(l=0, r=0, t=50, b=0),
    }

    # Dimensionality Reduction Settings
    DEFAULT_N_COMPONENTS_3D = 3
    DEFAULT_N_COMPONENTS_2D = 2
    DEFAULT_RANDOM_STATE = 42

    # Available Methods
    REDUCTION_METHODS = [
        {"label": "PCA", "value": "pca"},
        {"label": "t-SNE", "value": "tsne"},
        {"label": "UMAP", "value": "umap"},
    ]

    COLOR_OPTIONS = [
        {"label": "Category", "value": "category"},
        {"label": "Subcategory", "value": "subcategory"},
        {"label": "Tags", "value": "tags"},
    ]

    DIMENSION_OPTIONS = [{"label": "2D", "value": "2d"}, {"label": "3D", "value": "3d"}]

    # Default Values
    DEFAULT_METHOD = "pca"
    DEFAULT_COLOR_BY = "category"
    DEFAULT_DIMENSIONS = "3d"
    DEFAULT_SHOW_PROMPTS = ["show"]

    # Plot Marker Settings
    DOCUMENT_MARKER_SIZE_2D = 8
    DOCUMENT_MARKER_SIZE_3D = 5
    PROMPT_MARKER_SIZE_2D = 10
    PROMPT_MARKER_SIZE_3D = 6

    DOCUMENT_MARKER_SYMBOL = "circle"
    PROMPT_MARKER_SYMBOL = "diamond"

    DOCUMENT_OPACITY = 1.0
    PROMPT_OPACITY = 0.8

    # Text Processing
    TEXT_PREVIEW_LENGTH = 100

    # App Configuration
    DEBUG = os.getenv("EMBEDDINGBUDDY_DEBUG", "False").lower() == "true"
    HOST = os.getenv("EMBEDDINGBUDDY_HOST", "127.0.0.1")
    PORT = int(os.getenv("EMBEDDINGBUDDY_PORT", "8050"))

    # Environment Configuration
    ENVIRONMENT = os.getenv(
        "EMBEDDINGBUDDY_ENV", "development"
    )  # development, production

    # WSGI Server Configuration (for production)
    GUNICORN_WORKERS = int(os.getenv("GUNICORN_WORKERS", "4"))
    GUNICORN_BIND = os.getenv("GUNICORN_BIND", f"{HOST}:{PORT}")
    GUNICORN_TIMEOUT = int(os.getenv("GUNICORN_TIMEOUT", "120"))
    GUNICORN_KEEPALIVE = int(os.getenv("GUNICORN_KEEPALIVE", "5"))

    # OpenSearch Configuration
    OPENSEARCH_ENABLED = (
        os.getenv("EMBEDDINGBUDDY_OPENSEARCH_ENABLED", "True").lower() == "true"
    )
    OPENSEARCH_DEFAULT_SIZE = 100
    OPENSEARCH_SAMPLE_SIZE = 5
    OPENSEARCH_CONNECTION_TIMEOUT = 30
    OPENSEARCH_VERIFY_CERTS = True

    # Text Input / Transformers.js Configuration
    DEFAULT_EMBEDDING_MODEL = "Xenova/all-mpnet-base-v2"
    MAX_TEXT_LENGTH = 50000  # Characters (browser memory limits)
    DEFAULT_TOKENIZATION_METHOD = "sentence"
    MAX_BATCH_SIZE = 8  # Process in smaller batches for memory management

    # Available Transformers.js compatible models
    AVAILABLE_MODELS = [
        {
            "name": "Xenova/all-mpnet-base-v2",
            "label": "All-MPNet-Base-v2 (Quality, 768d)",
            "description": "Higher quality embeddings with better semantic understanding",
            "dimensions": 768,
            "size": "109 MB",
            "context_length": 512,
            "multilingual": False,
            "default": True,
        },
        {
            "name": "Xenova/all-MiniLM-L6-v2",
            "label": "All-MiniLM-L6-v2 (Fast, 384d)",
            "description": "Lightweight model, good for quick testing and general purpose",
            "dimensions": 384,
            "size": "23 MB",
            "context_length": 512,
            "multilingual": False,
            "default": False,
        },
        {
            "name": "Xenova/paraphrase-multilingual-MiniLM-L12-v2",
            "label": "Multilingual MiniLM (50+ languages)",
            "description": "Support for multiple languages with good performance",
            "dimensions": 384,
            "size": "127 MB",
            "context_length": 512,
            "multilingual": True,
        },
        {
            "name": "Xenova/bge-small-en-v1.5",
            "label": "BGE Small English (High quality, 384d)",
            "description": "Beijing Academy of AI model with excellent performance on retrieval tasks",
            "dimensions": 384,
            "size": "67 MB",
            "context_length": 512,
            "multilingual": False,
        },
        {
            "name": "Xenova/gte-small",
            "label": "GTE Small (General Text Embeddings, 384d)",
            "description": "Alibaba's general text embedding model, balanced performance",
            "dimensions": 384,
            "size": "67 MB",
            "context_length": 512,
            "multilingual": False,
        },
    ]

    # Browser compatibility requirements
    SUPPORTED_BROWSERS = {
        "chrome": ">=88",
        "firefox": ">=92",
        "safari": ">=15.4",
        "edge": ">=88",
    }

    # Bootstrap Theme
    EXTERNAL_STYLESHEETS = [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
    ]

    @classmethod
    def get_plot_marker_config(
        cls, dimensions: str, is_prompt: bool = False
    ) -> Dict[str, Any]:
        if is_prompt:
            size = (
                cls.PROMPT_MARKER_SIZE_3D
                if dimensions == "3d"
                else cls.PROMPT_MARKER_SIZE_2D
            )
            symbol = cls.PROMPT_MARKER_SYMBOL
            opacity = cls.PROMPT_OPACITY
        else:
            size = (
                cls.DOCUMENT_MARKER_SIZE_3D
                if dimensions == "3d"
                else cls.DOCUMENT_MARKER_SIZE_2D
            )
            symbol = cls.DOCUMENT_MARKER_SYMBOL
            opacity = cls.DOCUMENT_OPACITY

        return {"size": size, "symbol": symbol, "opacity": opacity}
