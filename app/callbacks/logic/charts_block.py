import dash_bootstrap_components as dbc
from dash import dcc, dash_table, html


def create_charts_block(fig, df):
    stats_table = stats_accordion(df)
    switch_chart = switch_chart_mode()
    return dbc.Container([
        switch_chart,
        dcc.Graph(id="water_graph", figure=fig, config={"displayModeBar": True}),
        stats_table,
        html.Br()
        # dcc.Graph(id="water_graph", figure=fig1, config={"displayModeBar": True}),
        # dcc.Graph(id="water_graph", figure=fig2, config={"displayModeBar": True}),
        # dcc.Graph(id="water_graph", figure=fig3, config={"displayModeBar": True}),
    ], className="p-4 my-4 bg-light rounded shadow")


# Switch chart mode
def switch_chart_mode():
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
                        id="chart-mode",
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

