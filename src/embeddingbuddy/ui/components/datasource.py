from dash import dcc, html
import dash_bootstrap_components as dbc
from .upload import UploadComponent


class DataSourceComponent:
    def __init__(self):
        self.upload_component = UploadComponent()

    def create_tabbed_interface(self):
        """Create tabbed interface for different data sources."""
        return dbc.Card(
            [
                dbc.CardHeader(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(label="File Upload", tab_id="file-tab"),
                                dbc.Tab(label="OpenSearch", tab_id="opensearch-tab"),
                            ],
                            id="data-source-tabs",
                            active_tab="file-tab",
                        )
                    ]
                ),
                dbc.CardBody([html.Div(id="tab-content")]),
            ]
        )

    def create_file_upload_tab(self):
        """Create file upload tab content."""
        return html.Div(
            [
                self.upload_component.create_error_alert(),
                self.upload_component.create_data_upload(),
                self.upload_component.create_prompts_upload(),
                self.upload_component.create_reset_button(),
            ]
        )

    def create_opensearch_tab(self):
        """Create OpenSearch tab content."""
        return html.Div(
            [
                # Connection section
                html.H6("Connection", className="mb-2"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("OpenSearch URL:"),
                                dbc.Input(
                                    id="opensearch-url",
                                    type="text",
                                    placeholder="https://opensearch.example.com:9200",
                                    className="mb-2",
                                ),
                            ],
                            width=12,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Index Name:"),
                                dbc.Input(
                                    id="opensearch-index",
                                    type="text",
                                    placeholder="my-embeddings-index",
                                    className="mb-2",
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Test Connection",
                                    id="test-connection-btn",
                                    color="primary",
                                    size="sm",
                                    className="mt-4",
                                ),
                            ],
                            width=6,
                            className="d-flex align-items-end",
                        ),
                    ]
                ),
                # Authentication section (collapsible)
                dbc.Collapse(
                    [
                        html.Hr(),
                        html.H6("Authentication (Optional)", className="mb-2"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("Username:"),
                                        dbc.Input(
                                            id="opensearch-username",
                                            type="text",
                                            className="mb-2",
                                        ),
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("Password:"),
                                        dbc.Input(
                                            id="opensearch-password",
                                            type="password",
                                            className="mb-2",
                                        ),
                                    ],
                                    width=6,
                                ),
                            ]
                        ),
                        dbc.Label("OR"),
                        dbc.Input(
                            id="opensearch-api-key",
                            type="text",
                            placeholder="API Key",
                            className="mb-2",
                        ),
                    ],
                    id="auth-collapse",
                    is_open=False,
                ),
                dbc.Button(
                    "Show Authentication",
                    id="auth-toggle",
                    color="link",
                    size="sm",
                    className="p-0 mb-3",
                ),
                # Connection status
                html.Div(id="connection-status", className="mb-3"),
                # Field mapping section (hidden initially)
                html.Div(id="field-mapping-section", style={"display": "none"}),
                
                # Hidden dropdowns to prevent callback errors
                html.Div([
                    dcc.Dropdown(id="embedding-field-dropdown", style={"display": "none"}),
                    dcc.Dropdown(id="text-field-dropdown", style={"display": "none"}),
                    dcc.Dropdown(id="id-field-dropdown", style={"display": "none"}),
                    dcc.Dropdown(id="category-field-dropdown", style={"display": "none"}),
                    dcc.Dropdown(id="subcategory-field-dropdown", style={"display": "none"}),
                    dcc.Dropdown(id="tags-field-dropdown", style={"display": "none"}),
                ], style={"display": "none"}),
                # Load data button (hidden initially)
                html.Div(
                    [
                        dbc.Button(
                            "Load Data",
                            id="load-opensearch-data-btn",
                            color="success",
                            className="mb-2",
                            disabled=True,
                        ),
                    ],
                    id="load-data-section",
                    style={"display": "none"},
                ),
                # OpenSearch status/results
                html.Div(id="opensearch-status", className="mb-3"),
            ]
        )

    def create_field_mapping_interface(self, field_suggestions):
        """Create field mapping interface based on detected fields."""
        return html.Div(
            [
                html.Hr(),
                html.H6("Field Mapping", className="mb-2"),
                html.P(
                    "Map your OpenSearch fields to the required format:",
                    className="text-muted small",
                ),
                # Required fields
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label(
                                    "Embedding Field (required):", className="fw-bold"
                                ),
                                dcc.Dropdown(
                                    id="embedding-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get("embedding", [])
                                    ],
                                    value=field_suggestions.get("embedding", [None])[0],  # Default to first suggestion
                                    placeholder="Select embedding field...",
                                    className="mb-2",
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label(
                                    "Text Field (required):", className="fw-bold"
                                ),
                                dcc.Dropdown(
                                    id="text-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get("text", [])
                                    ],
                                    value=field_suggestions.get("text", [None])[0],  # Default to first suggestion
                                    placeholder="Select text field...",
                                    className="mb-2",
                                ),
                            ],
                            width=6,
                        ),
                    ]
                ),
                # Optional fields
                html.H6("Optional Fields", className="mb-2 mt-3"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("ID Field:"),
                                dcc.Dropdown(
                                    id="id-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get("id", [])
                                    ],
                                    value=field_suggestions.get("id", [None])[0],  # Default to first suggestion
                                    placeholder="Select ID field...",
                                    className="mb-2",
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Category Field:"),
                                dcc.Dropdown(
                                    id="category-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get("category", [])
                                    ],
                                    value=field_suggestions.get("category", [None])[0],  # Default to first suggestion
                                    placeholder="Select category field...",
                                    className="mb-2",
                                ),
                            ],
                            width=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Subcategory Field:"),
                                dcc.Dropdown(
                                    id="subcategory-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get("subcategory", [])
                                    ],
                                    value=field_suggestions.get("subcategory", [None])[0],  # Default to first suggestion
                                    placeholder="Select subcategory field...",
                                    className="mb-2",
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Tags Field:"),
                                dcc.Dropdown(
                                    id="tags-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get("tags", [])
                                    ],
                                    value=field_suggestions.get("tags", [None])[0],  # Default to first suggestion
                                    placeholder="Select tags field...",
                                    className="mb-2",
                                ),
                            ],
                            width=6,
                        ),
                    ]
                ),
            ]
        )

    def create_error_alert(self):
        """Create error alert component for OpenSearch issues."""
        return dbc.Alert(
            id="opensearch-error-alert",
            dismissable=True,
            is_open=False,
            color="danger",
            className="mb-3",
        )

    def create_success_alert(self):
        """Create success alert component for OpenSearch operations."""
        return dbc.Alert(
            id="opensearch-success-alert",
            dismissable=True,
            is_open=False,
            color="success",
            className="mb-3",
        )
