from app.callbacks.simulation_callbacks import register_simulation_callbacks
from app.callbacks.slider_callbacks import register_slider_callbacks


def register_callbacks(app):
    register_slider_callbacks(app)
    register_simulation_callbacks(app)