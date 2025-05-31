import dash_bootstrap_components as dbc
from dash import dcc, dash_table, html


def create_charts_block(fig_pi, df_pi, fig_fuzzy, df_fuzzy, comparison_fig, comparison_fig_percentage,
                        comparison_fig_difference, comp_fig):
    switch_chart_pi = switch_chart_mode()
    switch_chart_fuzzy = switch_chart_mode(callback_id='chart-mode-fuzzy')

    stats_table_pi = stats_accordion(df_pi)
    stats_table_fuzzy = stats_accordion(df_fuzzy)
    return dbc.Container([

        # === KARTA: REGULATOR PI ===
        dbc.Card([
            dbc.CardHeader("🔧 Regulator PI", className="fs-4 fw-bold text-primary"),
            dbc.CardBody([
                switch_chart_pi,
                dcc.Graph(id="water_graph_pi", figure=fig_pi, config={"displayModeBar": True}),
                stats_table_pi
            ])
        ], className="mb-4 shadow-sm"),

        # === KARTA: REGULATOR FUZZY ===
        dbc.Card([
            dbc.CardHeader("🔧 Regulator rozmyty", className="fs-4 fw-bold text-primary"),
            dbc.CardBody([
                switch_chart_fuzzy,
                dcc.Graph(id="water_graph_fuzzy", figure=fig_fuzzy, config={"displayModeBar": True}),
                stats_table_fuzzy
            ])
        ], className="mb-4 shadow-sm"),

        dbc.Card([
            dbc.CardHeader("📊 Porównanie regulatorów", className="fs-4 fw-bold text-dark"),
            dbc.CardBody([
                dcc.Graph(id="comparison_graph_1", figure=comp_fig, config={"displayModeBar": True}),
                dcc.Graph(id="comparison_graph_normal", figure=comparison_fig, config={"displayModeBar": True}),
                dcc.Graph(id="comparison_graph_percentage", figure=comparison_fig_percentage, config={"displayModeBar": True}),
                #dcc.Graph(id="comparison_graph_difference", figure=comparison_fig_difference, config={"displayModeBar": True}),
            ])
        ], className="mb-4 shadow-sm"),

    ], className="p-4 my-4 bg-light rounded shadow")


# Switch chart mode
def switch_chart_mode(callback_id='chart-mode-pi'):
    return dbc.Container([
        dbc.Row(
            dbc.Col(
                html.Div("Wybierz tryb wykresu", className="text-center mb-2 fw-semibold"),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.ButtonGroup([
                    dbc.RadioItems(
                        id=callback_id,
                        options=[
                            {"label": "Statyczny", "value": "static"},
                            {"label": "Animacja", "value": "animated"},
                        ],
                        value="static",
                        inline=True,
                        labelCheckedClassName="active",
                        inputClassName="btn-check",
                        labelClassName="btn btn-outline-info",
                    )
                ]),
                className="d-flex justify-content-center"
            )
        )
    ],
        className="mb-4"
    )


# Data table for stats
def create_data_table(df):
    numeric_cols = ['rainfall_amount', 'water_amount', 'pumped_up_water', 'pumped_out_water', 'saved_water']

    # Przetwarzanie danych
    stats_df = df[numeric_cols].describe().round(2).reset_index()

    # Mapowanie nazw kolumn na polskie
    translation_map = {
        'index': 'Statystyka',
        'rainfall_amount': 'Opad [mm]',
        'water_amount': 'Poziom wody [L]',
        'pumped_up_water': 'Wpompowana woda [L]',
        'pumped_out_water': 'Zużyta woda [L]',
        'saved_water': 'Zaoszczędzona woda [L]'
    }

    # Tłumaczenie nazw kolumn
    columns = [{"name": translation_map.get(col, col), "id": col} for col in stats_df.columns]

    return dash_table.DataTable(
        columns=columns,
        data=stats_df.to_dict("records"),
        style_table={
            'overflowX': 'auto',
            'border': '1px solid #ccc',
            'marginTop': '20px'
        },
        style_cell={
            'padding': '8px',
            'textAlign': 'center',
            'fontFamily': 'Arial',
            'fontSize': '14px',
            'border': '1px solid #eee',
        },
        style_header={
            'backgroundColor': '#f0f0f0',
            'fontWeight': 'bold',
            'borderBottom': '2px solid #ccc',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#fafafa',
            }
        ],
    )


# Accordion for stats
def stats_accordion(df):
    return dbc.Accordion(
        [
            dbc.AccordionItem(
                children=create_data_table(df),
                title=html.Div(
                    "📊 Szczegółowe dane symulacji",
                    className="text-center fw-semibold",
                    style={"width": "100%"}
                ),
                className="bg-light"
            )
        ],
        start_collapsed=True,
        className="mb-4 shadow-sm rounded border border-secondary-subtle bg-white",
        flush=False
    )
