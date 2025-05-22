import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import requests
from dash import Input, Output, State, dcc

from app.layout.layouts import toast_success_status, toast_error_status


def register_callbacks(app):
    # Callback to update data in cards from sliders values
    @app.callback(
        Output("card-tank", "children"),
        Output("card-min", "children"),
        Output("card-daily", "children"),
        Output("card-roof", "children"),
        Input("slider-tank-capacity", "value"),
        Input("slider-min-level", "value"),
        Input("slider-daily-use", "value"),
        Input("slider-roof-area", "value"),
    )
    def update_cards(tank, min_level, daily_use, roof_area):
        return f"{tank} L", f"{min_level} L", f"{daily_use} L", f"{roof_area} m²"

    # API request in JSON form
    @app.callback(
        Output("simulation-output", "children"),  # komunikat
        Output("water-graph", "children"),  # wykres
        Input("simulate-button", "n_clicks"),
        State("dropdown-city", "value"),
        State("slider-tank-capacity", "value"),
        State("slider-min-level", "value"),
        State("slider-daily-use", "value"),
        State("slider-roof-area", "value"),
        prevent_initial_call=True,
    )
    def run_simulation(n_clicks, location, tank_capacity, min_water_level, daily_use, roof_area):
        if not all([tank_capacity, min_water_level, daily_use, roof_area, location]):
            return "Wypełnij wszystkie pola przed symulacją.", None

        # Dane w formacie JSON
        payload = {
            "tank_capacity": tank_capacity,
            "min_water_level": min_water_level,
            "daily_water_usage": daily_use,
            "rooftop_size": roof_area,
            "location": location,
        }

        try:
            response = requests.post("http://localhost:5000/api/simulation", json=payload)
            if response.status_code == 200:
                results = response.json()

                # Dane dla plotly
                df = pd.DataFrame(results)

                # Wykres
                title = f"Poziom wody - min: {df['water_amount'].min()}, max: {df['water_amount'].max()}"
                fig = px.line(
                    df,
                    x="date",
                    y="water_amount",
                    title=title,
                    labels={"value": "Poziom wody [L]", "variable": "Typ"},
                    markers=True
                )

                # Pozioma linia – minimalny poziom wody
                fig.add_hline(
                    y=min_water_level,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Min. poziom: {min_water_level} L",
                    annotation_position="bottom right",
                    annotation_font_size=12,
                    opacity=0.8
                )

                return (
                    toast_success_status("✅ Symulacja zakończona sukcesem."),
                    dbc.Container([
                        dcc.Graph(id="water_graph", figure=fig, config={"displayModeBar": True})
                    ], className="p-4 my-4 bg-light rounded shadow"),
                )

            else:
                return toast_error_status(f"❌ Błąd: {response.json().get('error', 'Nieznany problem')}"), None
        except Exception as e:
            return toast_error_status(f"❌ Błąd połączenia z API: {str(e)}"), None