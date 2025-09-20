from dash import dcc, html
import dash_bootstrap_components as dbc
from .upload import UploadComponent
from .datasource import DataSourceComponent
from .textinput import TextInputComponent
from embeddingbuddy.config.settings import AppSettings


class SidebarComponent:
    def __init__(self):
        self.upload_component = UploadComponent()
        self.datasource_component = DataSourceComponent()
        self.textinput_component = TextInputComponent()

    def create_layout(self):
        return dbc.Col(
            [
                dbc.Accordion(
                    [
                        self._create_data_sources_item(),
                        self._create_generate_embeddings_item(),
                        self._create_visualization_controls_item(),
                    ],
                    always_open=True,
                )
            ],
            width=3,
            style={"padding-right": "20px"},
        )

    def _create_method_dropdown(self):
        return [
            dbc.Label("Method:"),
            dcc.Dropdown(
                id="method-dropdown",
                options=[
                    {"label": "PCA", "value": "pca"},
                    {"label": "t-SNE", "value": "tsne"},
                    {"label": "UMAP", "value": "umap"},
                ],
                value="pca",
                style={"margin-bottom": "15px"},
            ),
        ]

    def _create_color_dropdown(self):
        return [
            dbc.Label("Color by:"),
            dcc.Dropdown(
                id="color-dropdown",
                options=[
                    {"label": "Category", "value": "category"},
                    {"label": "Subcategory", "value": "subcategory"},
                    {"label": "Tags", "value": "tags"},
                ],
                value="category",
                style={"margin-bottom": "15px"},
            ),
        ]

    def _create_dimension_toggle(self):
        return [
            dbc.Label("Dimensions:"),
            dcc.RadioItems(
                id="dimension-toggle",
                options=[
                    {"label": "2D", "value": "2d"},
                    {"label": "3D", "value": "3d"},
                ],
                value="3d",
                style={"margin-bottom": "20px"},
            ),
        ]

    def _create_prompts_toggle(self):
        return [
            dbc.Label("Show Prompts:"),
            dcc.Checklist(
                id="show-prompts-toggle",
                options=[{"label": "Show prompts on plot", "value": "show"}],
                value=["show"],
                style={"margin-bottom": "20px"},
            ),
        ]

    def _create_generate_embeddings_item(self):
        return dbc.AccordionItem(
            [
                self.textinput_component.create_text_input_interface(),
            ],
            title=html.Span(
                [
                    "Generate Embeddings ",
                    html.I(
                        className="fas fa-info-circle text-muted",
                        style={"cursor": "pointer"},
                        id="generate-embeddings-info-icon",
                        title="Create new embeddings from text input using various in-browser models",
                    ),
                ]
            ),
            item_id="generate-embeddings-accordion",
        )

    def _create_data_sources_item(self):
        tooltip_text = "Load existing embeddings: upload files"
        if AppSettings.OPENSEARCH_ENABLED:
            tooltip_text += " or read from OpenSearch"

        return dbc.AccordionItem(
            [
                self.datasource_component.create_error_alert(),
                self.datasource_component.create_success_alert(),
                self.datasource_component.create_tabbed_interface(),
            ],
            title=html.Span(
                [
                    "Load Embeddings ",
                    html.I(
                        className="fas fa-info-circle text-muted",
                        style={"cursor": "pointer"},
                        id="load-embeddings-info-icon",
                        title=tooltip_text,
                    ),
                ]
            ),
            item_id="data-sources-accordion",
        )

    def _create_visualization_controls_item(self):
        return dbc.AccordionItem(
            self._create_method_dropdown()
            + self._create_color_dropdown()
            + self._create_dimension_toggle()
            + self._create_prompts_toggle(),
            title=html.Span(
                [
                    "Visualization Controls ",
                    html.I(
                        className="fas fa-info-circle text-muted",
                        style={"cursor": "pointer"},
                        id="visualization-controls-info-icon",
                        title="Configure plot settings: select dimensionality reduction method, colors, and display options",
                    ),
                ]
            ),
            item_id="visualization-controls-accordion",
        )
