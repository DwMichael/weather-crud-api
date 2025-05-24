from dash import Input, Output, State

from app.callbacks.logic.charts import generate_static_chart, generate_animation_chart
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
            df, df_long = process_simulation_data(results)
            fig = generate_static_chart(df_long)
            chart_block = create_charts_block(fig, df)
            return (
                toast_success_status("✅ Symulacja zakończona sukcesem."),
                chart_block,
                results,
            )
        except Exception as e:
            return toast_error_status(str(e)), None, None

        # # Dane w formacie JSON
        # payload = {
        #     "tank_capacity": tank_capacity,
        #     "min_water_level": min_water_level,
        #     "daily_water_usage": daily_use,
        #     "rooftop_size": roof_area,
        #     "location": location,
        # }
        #
        # try:
        #     response = requests.post("http://localhost:5000/api/simulation", json=payload)
        #     if response.status_code == 200:
        #         results = response.json()
        #
        #         # Dane dla plotly
        #         df = pd.DataFrame(results)
        #
        #         df['date'] = pd.to_datetime(df['date'])
        #
        #         # 1. Przekształć dane
        #         df_long = df.melt(
        #             id_vars='date',
        #             value_vars=['water_amount', 'pumped_up_water', 'pumped_out_water', 'saved_water'],
        #             var_name='type',
        #             value_name='value'
        #         )
        #
        #         # 2. Zmieniamy pumped_out_water na wartości ujemne
        #         df_long.loc[df_long['type'] == 'pumped_out_water', 'value'] *= -1
        #
        #         # 3. Zamień nazwy typów na po polsku (dla wyświetlania)
        #         translation_map = {
        #             'water_amount': 'Poziom wody [L]',
        #             'pumped_up_water': 'Wpompowana woda [L]',
        #             'pumped_out_water': 'Zużyta woda [L]',
        #             'saved_water': 'Zaoszczędzona woda [L]'
        #         }
        #         df_long['type'] = df_long['type'].map(translation_map)
        #
        #         # Wykres
        #         title = f"Poziom wody - min: {df['water_amount'].min()}, max: {df['water_amount'].max()}"
        #         fig = px.bar(
        #             df_long,
        #             x='type',
        #             y='value',
        #             color='type',
        #             animation_frame=df_long['date'].dt.strftime('%Y-%m-%d'),  # animacja po dacie
        #             title=f"Poziom wody - min: {df['water_amount'].min()}, max: {df['water_amount'].max()}",
        #             barmode="relative",
        #             labels={"value": "Objętość [L]", "type": "Rodzaj"},
        #             color_discrete_map={
        #                 'Poziom wody [L]': 'blue',
        #                 'Wpompowana woda [L]': 'green',
        #                 'Zużyta woda [L]': 'red',
        #                 'Zaoszczędzona woda [L]': '#00BFA9'
        #             },
        #         )
        #
        #         fig_static = px.bar(
        #             df_long,
        #             x='date',
        #             y='value',
        #             color='type',
        #             title="Podsumowanie całego okresu",
        #             barmode="relative",
        #             labels={"value": "Objętość [L]", "date": "Data", "type": "Rodzaj"},
        #             color_discrete_map={
        #                 'Poziom wody [L]': 'blue',
        #                 'Wpompowana woda [L]': 'green',
        #                 'Zużyta woda [L]': 'red',
        #                 'Zaoszczędzona woda [L]': '#00BFA9'
        #             },
        #         )
        #
        #         fig.update_layout(
        #             xaxis_title='Data',
        #             yaxis_title='Objętość [L]',
        #             legend_title='Rodzaj',
        #             hovermode='x unified',
        #             bargap=0.2
        #         )
        #
        #         # ilość zaoszczędzona wody w czasie
        #         # fig1 = go.Figure()
        #         # fig1.add_trace(go.Scatter(
        #         #     x=df['date'], y=df['water_amount'],
        #         #     name='Poziom wody', mode='lines+markers',
        #         #     yaxis='y1', line=dict(color='blue')
        #         # ))
        #         # fig1.add_trace(go.Bar(
        #         #     x=df['date'], y=df['saved_water'],
        #         #     name='Zaoszczędzona woda', yaxis='y2', marker_color='#00BFA9'
        #         # ))
        #         # fig1.update_layout(
        #         #     title="Poziom wody i zaoszczędzona woda",
        #         #     yaxis=dict(title='Poziom wody [L]'),
        #         #     yaxis2=dict(title='Zaoszczędzona woda [L]', overlaying='y', side='right'),
        #         #     barmode='relative'
        #         # )
        #
        #         # Heatmap -> ilość opadów deszczu w dniach
        #
        #         # df['day'] = df['date'].dt.day
        #         # df['month'] = df['date'].dt.month
        #         #
        #         # fig2 = px.density_heatmap(
        #         #     df,
        #         #     x='day',
        #         #     y='month',
        #         #     z='rainfall_amount',
        #         #     title='Opady deszczu – kalendarz cieplny',
        #         #     color_continuous_scale='Blues'
        #         # )
        #
        #         # Zakładamy, że masz df z kolumnami 'date' (datetime) i 'water_amount'
        #         # df = df.sort_values('date')
        #         # df = df.set_index('date')  # ustawienie daty jako indeksu
        #         #
        #         # # Dodaj daty co godzinę między dniami
        #         # df_hourly = df.resample('1H').interpolate(method='linear')
        #         #
        #         # # Sprawdź wynik
        #         # #print(df_hourly.head(48))  # pokazuje 2 dni po 24h
        #         #
        #         # # Reset indeksu jeśli chcesz wrócić do normalnej kolumny
        #         # df_hourly = df_hourly.reset_index()
        #         #
        #         # fig3 = px.line(
        #         #     df_hourly,
        #         #     x='date',
        #         #     y='water_amount',
        #         #     title="Interpolowany poziom wody co godzinę",
        #         #     labels={'date': 'Data i godzina', 'water_amount': 'Poziom wody [L]'}
        #         # )
        #
        #         numeric_cols = ['rainfall_amount', 'water_amount', 'pumped_up_water', 'pumped_out_water', 'saved_water']
        #         stats_df = df[numeric_cols].describe().round(2).reset_index()
        #         stats_table = dash_table.DataTable(
        #             columns=[{"name": i, "id": i} for i in stats_df.columns],
        #             data=stats_df.to_dict("records"),
        #             style_table={
        #                 'overflowX': 'auto',
        #                 'border': '1px solid #ccc',
        #                 'marginTop': '20px'
        #             },
        #             style_cell={
        #                 'padding': '8px',
        #                 'textAlign': 'center',
        #                 'fontFamily': 'Arial',
        #                 'fontSize': '14px',
        #                 'border': '1px solid #eee',
        #             },
        #             style_header={
        #                 'backgroundColor': '#f0f0f0',
        #                 'fontWeight': 'bold',
        #                 'borderBottom': '2px solid #ccc',
        #             },
        #             style_data_conditional=[
        #                 {
        #                     'if': {'row_index': 'odd'},
        #                     'backgroundColor': '#fafafa',
        #                 }
        #             ],
        #         )
        #
        #         chart_block = dbc.Container([
        #             dcc.RadioItems(
        #                 id='chart-mode',
        #                 options=[
        #                     {'label': 'Animacja', 'value': 'animated'},
        #                     {'label': 'Statyczny', 'value': 'static'}
        #                 ],
        #                 value='animated',
        #                 labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        #             ),
        #
        #             dcc.Graph(id="water_graph", figure=fig_static, config={"displayModeBar": True}),
        #             stats_table,
        #             # dcc.Graph(id="water_graph", figure=fig1, config={"displayModeBar": True}),
        #             # dcc.Graph(id="water_graph", figure=fig2, config={"displayModeBar": True}),
        #             # dcc.Graph(id="water_graph", figure=fig3, config={"displayModeBar": True}),
        #         ], className="p-4 my-4 bg-light rounded shadow")
        #
        #         return (
        #             toast_success_status("✅ Symulacja zakończona sukcesem."),
        #             chart_block,
        #             results,
        #         )
        #
        #     else:
        #         return toast_error_status(f"❌ Błąd: {response.json().get('error', 'Nieznany problem')}"), None, None
        # except Exception as e:
        #     return toast_error_status(f"❌ Błąd połączenia z API: {str(e)}"), None, None

    @app.callback(
        Output("water_graph", "figure"),
        Input("chart-mode", "value"),
        State("simulation-data", "data")
    )
    def update_chart(chart_mode, data):
        if not data:
            return None

        df, df_long = process_simulation_data(data)

        if chart_mode == 'animated':
            fig = generate_animation_chart(df,df_long)
        else:
            fig = generate_static_chart(df_long)

        return fig

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