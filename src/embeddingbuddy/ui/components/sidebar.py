from dash import dcc, html
import dash_bootstrap_components as dbc
from .upload import UploadComponent
from .datasource import DataSourceComponent


class SidebarComponent:
    def __init__(self):
        self.upload_component = UploadComponent()
        self.datasource_component = DataSourceComponent()

    def create_layout(self):
        return dbc.Col(
            [
                html.H5("Data Sources", className="mb-3"),
                self.datasource_component.create_error_alert(),
                self.datasource_component.create_success_alert(),
                self.datasource_component.create_tabbed_interface(),
                html.H5("Visualization Controls", className="mb-3 mt-4"),
            ]
            + self._create_method_dropdown()
            + self._create_color_dropdown()
            + self._create_dimension_toggle()
            + self._create_prompts_toggle()
            + [
                html.H5("Point Details", className="mb-3"),
                html.Div(
                    id="point-details", children="Click on a point to see details"
                ),
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
