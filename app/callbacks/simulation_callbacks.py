from dash import Input, Output, State

from app.callbacks.logic.charts import generate_static_chart, generate_animation_chart, generate_total_comparison, \
    generate_percentage_comparison, generate_difference_chart, generate_comparison_subplots, generate_average_comparison
from app.callbacks.logic.charts_block import create_charts_block
from app.callbacks.logic.fetch_simulation_data import fetch_simulation_data
from app.callbacks.logic.process_simulation_data import process_simulation_data
from app.layout.layouts import toast_success_status, toast_error_status


def register_simulation_callbacks(app):
    # API request in JSON form
    @app.callback(
        Output("simulation-output", "children"),  # komunikat
        Output("water-graph", "children"),  # wykres
        Output("simulation-data", "data"),  # dane do Store
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
            return toast_error_status("Wypełnij wszystkie pola przed symulacją."), None, None

        try:
            results = fetch_simulation_data(location, tank_capacity, min_water_level, daily_use, roof_area)

            df, df_long = process_simulation_data(results.get('pi_controller_results'))
            df_fuzzy, df_fuzzy_long = process_simulation_data(results.get('fuzzy_controller_results'))

            fig_pi = generate_static_chart(df_long, "Poziom wody (Regulator PI)")
            fig_fuzzy = generate_static_chart(df_fuzzy_long, "Poziom wody (Regulator rozmyty)")

            comp_fig = generate_comparison_subplots(df_long, df_fuzzy_long)
            comparison_fig = generate_average_comparison(df_long, df_fuzzy_long)
            comparison_fig_percentage = generate_percentage_comparison(df_long, df_fuzzy_long)
            comparison_fig_difference = generate_difference_chart(df_long, df_fuzzy_long)

            chart_block = create_charts_block(fig_pi, df, fig_fuzzy, df_fuzzy, comparison_fig,
                                              comparison_fig_percentage, comparison_fig_difference, comp_fig)
            return (
                toast_success_status("✅ Symulacja zakończona sukcesem."),
                chart_block,
                results,
            )
        except Exception as e:
            return toast_error_status(str(e)), None, None

    @app.callback(
        Output("water_graph_pi", "figure"),
        Output("water_graph_fuzzy", "figure"),
        Input("chart-mode-pi", "value"),
        Input("chart-mode-fuzzy", "value"),
        State("simulation-data", "data")
    )
    def update_chart(chart_mode_pi, chart_mode_fuzzy, data):
        if not data:
            return None

        df_pi, df_pi_long = process_simulation_data(data.get('pi_controller_results'), chart_mode_pi)
        df_fuzzy, df_fuzzy_long = process_simulation_data(data.get('fuzzy_controller_results'), chart_mode_fuzzy)

        if chart_mode_pi == 'animated':
            fig = generate_animation_chart(df_pi, df_pi_long)
        else:
            fig = generate_static_chart(df_pi_long, "Poziom wody (Regulator PI)")

        if chart_mode_fuzzy == 'animated':
            fig_fuzzy = generate_animation_chart(df_fuzzy, df_fuzzy_long)
        else:
            fig_fuzzy = generate_static_chart(df_fuzzy_long, "Poziom wody (Regulator rozmyty)")

        return fig, fig_fuzzy

    @app.callback(
        Output("stats-collapse", "is_open"),
        Input("stats-toggle", "n_clicks"),
        State("stats-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_stats(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open
