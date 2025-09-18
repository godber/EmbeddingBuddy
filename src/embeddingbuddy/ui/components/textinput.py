"""Text input component for generating embeddings from user text."""

import dash_bootstrap_components as dbc
from dash import dcc, html

from embeddingbuddy.config.settings import AppSettings


class TextInputComponent:
    """Component for text input and embedding generation."""

    def __init__(self):
        self.settings = AppSettings()

    def create_text_input_interface(self):
        """Create the complete text input interface with model selection and processing options."""
        return html.Div(
            [
                # Text input section
                self._create_text_input_area(),
                # Text action buttons
                self._create_text_action_buttons(),
                html.Hr(),
                # Model selection section
                self._create_model_selection(),
                html.Hr(),
                # Processing options
                self._create_processing_options(),
                html.Hr(),
                # Generation controls
                self._create_generation_controls(),
                html.Hr(),
                # Status and results
                self._create_status_section(),
                # Hidden components for data flow
                self._create_hidden_components(),
            ],
            className="p-3",
        )

    def _create_model_selection(self):
        """Create model selection dropdown with descriptions."""
        model_options = []
        for model in self.settings.AVAILABLE_MODELS:
            label = f"{model['label']} - {model['size']}"
            if model.get("default", False):
                label += " (Recommended)"

            model_options.append({"label": label, "value": model["name"]})

        return html.Div(
            [
                html.H5("Embedding Model", className="mb-3"),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="model-selection",
                            options=model_options,
                            value=self.settings.DEFAULT_EMBEDDING_MODEL,
                            placeholder="Select an embedding model...",
                            className="mb-2",
                        ),
                        dbc.Alert(
                            [
                                html.Div(
                                    id="model-info",
                                    children=self._get_model_description(
                                        self.settings.DEFAULT_EMBEDDING_MODEL
                                    ),
                                )
                            ],
                            color="info",
                            className="small",
                        ),
                    ]
                ),
            ]
        )

    def _create_text_input_area(self):
        """Create text input textarea with character limits."""
        return html.Div(
            [
                html.H5("Text Input", className="mb-3"),
                dcc.Textarea(
                    id="text-input-area",
                    placeholder="Paste your text here... Each sentence, paragraph, or line will become a separate data point depending on your tokenization method below.",
                    value="",
                    style={
                        "width": "100%",
                        "height": "300px",
                        "resize": "vertical",
                        "font-family": "monospace",
                        "font-size": "14px",
                    },
                    maxLength=self.settings.MAX_TEXT_LENGTH,
                    className="form-control",
                ),
                html.Small(
                    f"Maximum {self.settings.MAX_TEXT_LENGTH:,} characters. Current: ",
                    className="text-muted",
                ),
                html.Small(
                    id="text-length-counter",
                    children="0",
                    className="text-muted fw-bold",
                ),
                html.Small(" characters", className="text-muted"),
            ]
        )

    def _create_text_action_buttons(self):
        """Create action buttons for text input (Load Sample, Clear)."""
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-file-text me-2"),
                                        "Load Sample Text",
                                    ],
                                    id="load-sample-btn",
                                    color="info",
                                    size="sm",
                                    className="w-100",
                                )
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-trash me-2"),
                                        "Clear Text",
                                    ],
                                    id="clear-text-btn",
                                    color="outline-secondary",
                                    size="sm",
                                    className="w-100",
                                )
                            ],
                            md=6,
                        ),
                    ],
                    className="mt-2 mb-3",
                )
            ]
        )

    def _create_processing_options(self):
        """Create tokenization and metadata options."""
        return html.Div(
            [
                html.H5("Processing Options", className="mb-3"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label(
                                    "Text Splitting Method:", className="form-label"
                                ),
                                dcc.Dropdown(
                                    id="tokenization-method",
                                    options=[
                                        {
                                            "label": "Sentences (split on . ! ?)",
                                            "value": "sentence",
                                        },
                                        {
                                            "label": "Paragraphs (split on double newline)",
                                            "value": "paragraph",
                                        },
                                        {
                                            "label": "Lines (split on single newline)",
                                            "value": "manual",
                                        },
                                        {
                                            "label": "Entire text as one document",
                                            "value": "whole",
                                        },
                                    ],
                                    value=self.settings.DEFAULT_TOKENIZATION_METHOD,
                                    className="mb-3",
                                ),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                html.Label("Batch Size:", className="form-label"),
                                dcc.Dropdown(
                                    id="batch-size",
                                    options=[
                                        {
                                            "label": "Small batches (4) - Lower memory",
                                            "value": 4,
                                        },
                                        {
                                            "label": "Medium batches (8) - Balanced",
                                            "value": 8,
                                        },
                                        {
                                            "label": "Large batches (16) - Faster",
                                            "value": 16,
                                        },
                                    ],
                                    value=self.settings.MAX_BATCH_SIZE,
                                    className="mb-3",
                                ),
                            ],
                            md=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label(
                                    "Category (Optional):", className="form-label"
                                ),
                                dcc.Input(
                                    id="text-category",
                                    type="text",
                                    placeholder="e.g., Notes, Articles, Ideas...",
                                    value="Text Input",
                                    className="form-control mb-3",
                                ),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                html.Label(
                                    "Subcategory (Optional):", className="form-label"
                                ),
                                dcc.Input(
                                    id="text-subcategory",
                                    type="text",
                                    placeholder="e.g., Meeting Notes, Research...",
                                    value="Generated",
                                    className="form-control mb-3",
                                ),
                            ],
                            md=6,
                        ),
                    ]
                ),
            ]
        )

    def _create_generation_controls(self):
        """Create embedding generation button and controls."""
        return html.Div(
            [
                html.H5("Generate Embeddings", className="mb-3"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-magic me-2"),
                                        "Generate Embeddings",
                                    ],
                                    id="generate-embeddings-btn",
                                    color="primary",
                                    size="lg",
                                    disabled=True,
                                    className="w-100",
                                )
                            ],
                            md=12,
                        ),
                    ]
                ),
                html.Div(
                    [
                        dbc.Alert(
                            [
                                html.I(className="fas fa-info-circle me-2"),
                                "Enter some text above and select a model to enable embedding generation.",
                            ],
                            color="light",
                            className="mt-3",
                            id="generation-help",
                        )
                    ]
                ),
            ]
        )

    def _create_status_section(self):
        """Create status alerts and results preview."""
        return html.Div(
            [
                # Server-side status
                dbc.Alert(
                    id="text-input-status",
                    children="",
                    color="light",
                    className="mb-3",
                    style={"display": "none"},
                ),
                # Results preview
                html.Div(id="embedding-results-preview"),
            ]
        )

    def _create_hidden_components(self):
        """Create hidden components for data flow."""
        return html.Div(
            [
                # Store for embeddings data from client-side
                dcc.Store(id="embeddings-generated-trigger"),
                # Store for tokenization preview
                dcc.Store(id="tokenization-preview-data"),
            ]
        )

    def _get_model_description(self, model_name):
        """Get description for a specific model."""
        for model in self.settings.AVAILABLE_MODELS:
            if model["name"] == model_name:
                return html.Div(
                    [
                        html.Strong(
                            f"Dimensions: {model['dimensions']} | Context Length: {model['context_length']}"
                        ),
                        html.Br(),
                        html.Span(model["description"]),
                        html.Br(),
                        html.Small(
                            f"Multilingual: {'Yes' if model.get('multilingual', False) else 'No'} | Size: {model['size']}",
                            className="text-muted",
                        ),
                    ]
                )

        return html.Span("Model information not available", className="text-muted")
