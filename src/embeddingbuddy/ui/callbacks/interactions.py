import dash
from dash import callback, Input, Output


class InteractionCallbacks:
    def __init__(self):
        self._register_callbacks()

    def _register_callbacks(self):
        @callback(
            Output("about-modal", "is_open"),
            [Input("about-button", "n_clicks"), Input("about-modal-close", "n_clicks")],
            prevent_initial_call=True,
        )
        def toggle_about_modal(about_clicks, close_clicks):
            if about_clicks or close_clicks:
                return True if about_clicks else False
            return False

        @callback(
            [
                Output("processed-data", "data", allow_duplicate=True),
                Output("processed-prompts", "data", allow_duplicate=True),
            ],
            Input("reset-button", "n_clicks"),
            prevent_initial_call=True,
        )
        def reset_data(n_clicks):
            if n_clicks is None or n_clicks == 0:
                return dash.no_update, dash.no_update

            return None, None
