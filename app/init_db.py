# app/init_db.py
from dash import Dash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import dash_bootstrap_components as dbc
from app.callbacks.init_callbacks import register_callbacks
from app.layout.layouts import main_layout

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from app.controllers.routes import routes_bp
    app.register_blueprint(routes_bp)

    with app.app_context():
        db.create_all()

    return app


def create_dash_app():
    # Tworzymy Flask server osobno
    server = Flask(__name__)
    server.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
    server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(server)

    from app.controllers.routes import routes_bp
    server.register_blueprint(routes_bp)

    with server.app_context():
        db.create_all()

    # Tworzymy Dash na bazie tego Flask
    app = Dash(__name__, server=server, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
    app.title = "Symulacja zbiornika"

    register_callbacks(app)
    app.layout = main_layout

    return app
