from dash import dcc, html
import dash_bootstrap_components as dbc
from .upload import UploadComponent
from embeddingbuddy.config.settings import AppSettings


class DataSourceComponent:
    def __init__(self):
        self.upload_component = UploadComponent()

    def create_tabbed_interface(self):
        """Create tabbed interface for different data sources."""
        tabs = [dbc.Tab(label="File Upload", tab_id="file-tab")]

        # Only add OpenSearch tab if enabled
        if AppSettings.OPENSEARCH_ENABLED:
            tabs.append(dbc.Tab(label="OpenSearch", tab_id="opensearch-tab"))

        return dbc.Card(
            [
                dbc.CardHeader(
                    [
                        dbc.Tabs(
                            tabs,
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
        """Create OpenSearch tab content with separate Data and Prompts sections."""
        return html.Div(
            [
                # Data Section
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                dbc.Button(
                                    [
                                        html.I(
                                            className="fas fa-chevron-down me-2",
                                            id="data-collapse-icon",
                                        ),
                                        "📄 Documents/Data",
                                    ],
                                    id="data-collapse-toggle",
                                    color="link",
                                    className="text-start p-0 w-100 text-decoration-none",
                                    style={
                                        "border": "none",
                                        "font-size": "1.25rem",
                                        "font-weight": "500",
                                    },
                                ),
                            ]
                        ),
                        dbc.Collapse(
                            [dbc.CardBody([self._create_opensearch_section("data")])],
                            id="data-collapse",
                            is_open=True,
                        ),
                    ],
                    className="mb-4",
                ),
                # Prompts Section
                dbc.Card(
                    [
                        dbc.CardHeader(
                            [
                                dbc.Button(
                                    [
                                        html.I(
                                            className="fas fa-chevron-down me-2",
                                            id="prompts-collapse-icon",
                                        ),
                                        "💬 Prompts",
                                    ],
                                    id="prompts-collapse-toggle",
                                    color="link",
                                    className="text-start p-0 w-100 text-decoration-none",
                                    style={
                                        "border": "none",
                                        "font-size": "1.25rem",
                                        "font-weight": "500",
                                    },
                                ),
                            ]
                        ),
                        dbc.Collapse(
                            [
                                dbc.CardBody(
                                    [self._create_opensearch_section("prompts")]
                                )
                            ],
                            id="prompts-collapse",
                            is_open=True,
                        ),
                    ],
                    className="mb-4",
                ),
                # Hidden dropdowns to prevent callback errors (for both sections)
                html.Div(
                    [
                        # Data dropdowns (hidden sync targets)
                        dcc.Dropdown(
                            id="data-embedding-field-dropdown",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="data-text-field-dropdown", style={"display": "none"}
                        ),
                        dcc.Dropdown(
                            id="data-id-field-dropdown", style={"display": "none"}
                        ),
                        dcc.Dropdown(
                            id="data-category-field-dropdown", style={"display": "none"}
                        ),
                        dcc.Dropdown(
                            id="data-subcategory-field-dropdown",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="data-tags-field-dropdown", style={"display": "none"}
                        ),
                        # Data UI dropdowns (hidden placeholders)
                        dcc.Dropdown(
                            id="data-embedding-field-dropdown-ui",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="data-text-field-dropdown-ui", style={"display": "none"}
                        ),
                        dcc.Dropdown(
                            id="data-id-field-dropdown-ui", style={"display": "none"}
                        ),
                        dcc.Dropdown(
                            id="data-category-field-dropdown-ui",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="data-subcategory-field-dropdown-ui",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="data-tags-field-dropdown-ui", style={"display": "none"}
                        ),
                        # Prompts dropdowns (hidden sync targets)
                        dcc.Dropdown(
                            id="prompts-embedding-field-dropdown",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="prompts-text-field-dropdown", style={"display": "none"}
                        ),
                        dcc.Dropdown(
                            id="prompts-id-field-dropdown", style={"display": "none"}
                        ),
                        dcc.Dropdown(
                            id="prompts-category-field-dropdown",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="prompts-subcategory-field-dropdown",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="prompts-tags-field-dropdown", style={"display": "none"}
                        ),
                        # Prompts UI dropdowns (hidden placeholders)
                        dcc.Dropdown(
                            id="prompts-embedding-field-dropdown-ui",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="prompts-text-field-dropdown-ui",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="prompts-id-field-dropdown-ui", style={"display": "none"}
                        ),
                        dcc.Dropdown(
                            id="prompts-category-field-dropdown-ui",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="prompts-subcategory-field-dropdown-ui",
                            style={"display": "none"},
                        ),
                        dcc.Dropdown(
                            id="prompts-tags-field-dropdown-ui",
                            style={"display": "none"},
                        ),
                    ],
                    style={"display": "none"},
                ),
            ]
        )

    def _create_opensearch_section(self, section_type):
        """Create a complete OpenSearch section for either 'data' or 'prompts'."""
        section_id = section_type  # 'data' or 'prompts'

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
                                    id=f"{section_id}-opensearch-url",
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
                                    id=f"{section_id}-opensearch-index",
                                    type="text",
                                    placeholder="my-embeddings-index",
                                    className="mb-2",
                                ),
                            ],
                            width=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Query Size:"),
                                dbc.Input(
                                    id=f"{section_id}-opensearch-query-size",
                                    type="number",
                                    value=100,
                                    min=1,
                                    max=1000,
                                    placeholder="100",
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
                                dbc.Button(
                                    "Test Connection",
                                    id=f"{section_id}-test-connection-btn",
                                    color="primary",
                                    className="mb-3",
                                ),
                            ],
                            width=12,
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
                                            id=f"{section_id}-opensearch-username",
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
                                            id=f"{section_id}-opensearch-password",
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
                            id=f"{section_id}-opensearch-api-key",
                            type="text",
                            placeholder="API Key",
                            className="mb-2",
                        ),
                    ],
                    id=f"{section_id}-auth-collapse",
                    is_open=False,
                ),
                dbc.Button(
                    "Show Authentication",
                    id=f"{section_id}-auth-toggle",
                    color="link",
                    size="sm",
                    className="p-0 mb-3",
                ),
                # Connection status
                html.Div(id=f"{section_id}-connection-status", className="mb-3"),
                # Field mapping section (hidden initially)
                html.Div(
                    id=f"{section_id}-field-mapping-section", style={"display": "none"}
                ),
                # Load data button (hidden initially)
                html.Div(
                    [
                        dbc.Button(
                            f"Load {section_type.title()}",
                            id=f"{section_id}-load-opensearch-data-btn",
                            color="success",
                            className="mb-2",
                            disabled=True,
                        ),
                    ],
                    id=f"{section_id}-load-data-section",
                    style={"display": "none"},
                ),
                # OpenSearch status/results
                html.Div(id=f"{section_id}-opensearch-status", className="mb-3"),
            ]
        )

    def create_field_mapping_interface(self, field_suggestions, section_type="data"):
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
                                    id=f"{section_type}-embedding-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get(
                                            "embedding", []
                                        )
                                    ],
                                    value=field_suggestions.get("embedding", [None])[
                                        0
                                    ],  # Default to first suggestion
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
                                    id=f"{section_type}-text-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get("text", [])
                                    ],
                                    value=field_suggestions.get("text", [None])[
                                        0
                                    ],  # Default to first suggestion
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
                                    id=f"{section_type}-id-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get("id", [])
                                    ],
                                    value=field_suggestions.get("id", [None])[
                                        0
                                    ],  # Default to first suggestion
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
                                    id=f"{section_type}-category-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get(
                                            "category", []
                                        )
                                    ],
                                    value=field_suggestions.get("category", [None])[
                                        0
                                    ],  # Default to first suggestion
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
                                    id=f"{section_type}-subcategory-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get(
                                            "subcategory", []
                                        )
                                    ],
                                    value=field_suggestions.get("subcategory", [None])[
                                        0
                                    ],  # Default to first suggestion
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
                                    id=f"{section_type}-tags-field-dropdown-ui",
                                    options=[
                                        {"label": field, "value": field}
                                        for field in field_suggestions.get("tags", [])
                                    ],
                                    value=field_suggestions.get("tags", [None])[
                                        0
                                    ],  # Default to first suggestion
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
