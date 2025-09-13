from dash import dcc, html
import dash_bootstrap_components as dbc


class UploadComponent:
    @staticmethod
    def create_data_upload():
        return html.Div(
            [
                dcc.Upload(
                    id="upload-data",
                    children=html.Div(
                        [
                            "Upload Data ",
                            html.I(
                                className="fas fa-info-circle",
                                style={"color": "#6c757d", "fontSize": "14px"},
                                id="data-upload-info",
                            ),
                        ]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin-bottom": "20px",
                    },
                    multiple=False,
                ),
                dbc.Tooltip(
                    "Click here or drag and drop NDJSON files containing document embeddings",
                    target="data-upload-info",
                    placement="top",
                ),
            ]
        )

    @staticmethod
    def create_prompts_upload():
        return html.Div(
            [
                dcc.Upload(
                    id="upload-prompts",
                    children=html.Div(
                        [
                            "Upload Prompts ",
                            html.I(
                                className="fas fa-info-circle",
                                style={"color": "#6c757d", "fontSize": "14px"},
                                id="prompts-upload-info",
                            ),
                        ]
                    ),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin-bottom": "20px",
                        "borderColor": "#28a745",
                    },
                    multiple=False,
                ),
                dbc.Tooltip(
                    "Click here or drag and drop NDJSON files containing prompt embeddings",
                    target="prompts-upload-info",
                    placement="top",
                ),
            ]
        )

    @staticmethod
    def create_reset_button():
        return dbc.Button(
            "Reset All Data",
            id="reset-button",
            color="danger",
            outline=True,
            size="sm",
            className="mb-3",
            style={"width": "100%"},
        )

    @staticmethod
    def create_error_alert():
        """Create error alert component for data upload issues."""
        return dbc.Alert(
            id="upload-error-alert",
            dismissable=True,
            is_open=False,
            color="danger",
            className="mb-3",
        )
