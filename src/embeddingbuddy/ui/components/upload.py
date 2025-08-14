from dash import dcc, html
import dash_bootstrap_components as dbc


class UploadComponent:
    @staticmethod
    def create_data_upload():
        return dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
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
        )

    @staticmethod
    def create_prompts_upload():
        return dcc.Upload(
            id="upload-prompts",
            children=html.Div(["Drag and Drop Prompts or ", html.A("Select Files")]),
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
