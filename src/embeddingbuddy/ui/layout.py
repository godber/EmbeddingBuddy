from dash import dcc, html
import dash_bootstrap_components as dbc
from .components.sidebar import SidebarComponent
from .components.about import AboutComponent


class AppLayout:
    def __init__(self):
        self.sidebar = SidebarComponent()
        self.about = AboutComponent()

    def create_layout(self):
        return dbc.Container(
            [self._create_header(), self._create_main_content()]
            + self._create_stores()
            + [self.about.create_about_modal()],
            fluid=True,
        )

    def _create_header(self):
        return dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H1(
                                    "EmbeddingBuddy",
                                    className="text-center mb-4 d-inline",
                                ),
                                html.Div(
                                    [self.about.create_about_button()],
                                    className="float-end",
                                ),
                            ],
                            className="d-flex justify-content-between align-items-center",
                        ),
                        # Load Transformers.js from CDN
                        html.Script(
                            """
                            import { pipeline } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.2';
                            window.transformersPipeline = pipeline;
                            console.log('✅ Transformers.js pipeline loaded globally');
                            """,
                            type="module",
                        ),
                    ],
                    width=12,
                )
            ]
        )

    def _create_main_content(self):
        return dbc.Row(
            [self.sidebar.create_layout(), self._create_visualization_area()]
        )

    def _create_visualization_area(self):
        return dbc.Col(
            [
                dcc.Graph(
                    id="embedding-plot",
                    style={"height": "85vh", "width": "100%"},
                    config={"responsive": True, "displayModeBar": True},
                )
            ],
            width=9,
        )

    def _create_stores(self):
        return [dcc.Store(id="processed-data"), dcc.Store(id="processed-prompts")]
