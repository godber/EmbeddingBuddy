import dash
import dash_bootstrap_components as dbc
from .config.settings import AppSettings
from .ui.layout import AppLayout
from .ui.callbacks.data_processing import DataProcessingCallbacks
from .ui.callbacks.visualization import VisualizationCallbacks
from .ui.callbacks.interactions import InteractionCallbacks


def create_app():
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Allow callbacks to components that are dynamically created in tabs
    app.config.suppress_callback_exceptions = True

    layout_manager = AppLayout()
    app.layout = layout_manager.create_layout()

    DataProcessingCallbacks()
    VisualizationCallbacks()
    InteractionCallbacks()

    return app


def run_app(app=None, debug=None, host=None, port=None):
    if app is None:
        app = create_app()

    app.run(
        debug=debug if debug is not None else AppSettings.DEBUG,
        host=host if host is not None else AppSettings.HOST,
        port=port if port is not None else AppSettings.PORT,
    )


if __name__ == "__main__":
    app = create_app()
    run_app(app)
