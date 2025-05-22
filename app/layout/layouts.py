import dash_bootstrap_components as dbc
from dash import html, dcc

import plotly.io as pio
pio.templates.default = "seaborn"

def navbar():
    # Navbar
    return dbc.Navbar(
        children=[
            dbc.Container([
                dbc.NavbarBrand(
                    "💧 Symulacja Zasobów Wody",
                    className="fw-bold text-white fs-4",
                    style={"paddingLeft": "4.5rem"}
                )
            ], fluid=False, style={"padding": "0"})
        ],
        color="primary",
        dark=True,
        className="mb-3 shadow-sm rounded-bottom",
        sticky="top"
    )

def welcome_section():
    # Welcome section
    return dbc.Row([
        dbc.Col([
            html.Div([
                # html.Div("💧", className="fs-1 mb-2"),  # Ikona dekoracyjna
                html.H2("Witamy!", className="display-5 fw-bold mb-3", style={
                    "fontFamily": "'Montserrat', sans-serif"
                }),
                html.H1(
                    "Symuluj zużycie wody na podstawie pojemności zbiornika, opadów i dziennego zapotrzebowania.",
                    className="lead text-white-50",
                    style={"fontFamily": "'Roboto', sans-serif"}
                )
            ],
                className="p-4 rounded-4 shadow",
                style={
                    "background": "linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%)",
                    "color": "white"
                })
        ], width=10, lg=6)
    ], justify="center", className="text-center my-4")
    #
    # html.Hr(),


def data_section_header():
    return html.H3("Parametry symulacji", className="text-center mb-4 mt-5",
                   style={"fontFamily": "'Montserrat', sans-serif"})


def simulation_section():
    return dbc.Container([

        # Location drop-down
        dbc.Row([
            dbc.Col([
                html.Label("📍 Wybierz miasto", className="fw-bold mb-2"),
                dcc.Dropdown(
                    id='dropdown-city',
                    options=[
                        {'label': 'Warszawa', 'value': 'Warszawa'},
                        {'label': 'Kraków', 'value': 'Kraków'},
                        {'label': 'Gdańsk', 'value': 'Gdańsk'},
                        {'label': 'Wrocław', 'value': 'Wrocław'},
                        {'label': 'Poznań', 'value': 'Poznań'},
                        {'label': 'Katowice', 'value': 'Katowice'},
                        {'label': 'Zakopane', 'value': 'Zakopane'}
                    ],
                    value='Poznań',
                    clearable=False,
                    className="mb-4",
                    style={"borderRadius": "8px"}  # zaokrąglone rogi dropdown
                )
            ], md=6, xs=12)
        ]),

        dbc.Row([

            # Tank capacity
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H2("🛢️", className="me-2 mb-0"),
                        "Pojemność zbiornika"
                    ], className="text-white d-flex align-items-center"),
                    dbc.CardBody([
                        html.H4("", id="card-tank", className="card-title text-white"),
                        html.P("Maksymalna ilość wody, jaką możesz przechowywać.", className="text-white-50")
                    ])
                ], style={"background": "linear-gradient(90deg, #4a6572, #1c3f52)"}, inverse=True,
                    className="shadow rounded p-3 mb-3"),

                html.Label("Pojemność zbiornika [L]", className="fw-bold mt-2 mb-2"),
                dcc.Slider(
                    id='slider-tank-capacity',
                    min=1000,
                    max=5000,
                    step=100,
                    value=3000,
                    marks={i: f"{i}" for i in range(1000, 5001, 500)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], md=6, xs=12, className="mb-4"),

            # Min water level
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H2("💦", className="me-2 mb-0"),
                        "Minimalny poziom wody w zbiorniku"
                    ], className="text-white d-flex align-items-center"),
                    dbc.CardBody([
                        html.H4("", id="card-min", className="card-title text-white"),
                        html.P("Minimalny poziom wody w zbiorniku.", className="text-white-50")
                    ])
                ], style={"background": "linear-gradient(90deg, #00b4db, #0083b0)"}, inverse=True,
                    className="shadow rounded p-3 mb-3"),

                html.Label("Minimalny poziom wody w zbiorniku [L]", className="fw-bold mt-2 mb-2"),
                dcc.Slider(
                    id='slider-min-level',
                    min=1,
                    max=3000,
                    step=1,
                    value=500,
                    marks={i: str(i) for i in [1, 250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000]},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], md=6, xs=12, className="mb-4")
        ]),

        dbc.Row([

            # Daily usage
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H2("🚿", className="me-2 mb-0"),
                        "Dzienne zużycie wody"
                    ], className="text-white d-flex align-items-center"),
                    dbc.CardBody([
                        html.H4("", id="card-daily", className="card-title text-white"),
                        html.P("Przeciętne dzienne zużycie wody.", className="text-white-50")
                    ])
                ], style={"background": "linear-gradient(90deg, #c31432, #240b36)"}, inverse=True,
                    className="shadow rounded p-3 mb-3"),

                html.Label("Dzienne zużycie wody [L]", className="fw-bold mt-2 mb-2"),
                dcc.Slider(
                    id='slider-daily-use',
                    min=1,
                    max=300,
                    step=1,
                    value=150,
                    marks={i: str(i) for i in [1, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300]},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], md=6, xs=12, className="mb-4"),

            # Roof area
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H2("🏡", className="me-2 mb-0"),
                        "Powierzchnia dachu"
                    ], className="text-white d-flex align-items-center"),
                    dbc.CardBody([
                        html.H4("", id="card-roof", className="card-title text-white"),
                        html.P("Szacowana powierzchnia dachu", className="text-white-50")
                    ])
                ], style={"background": "linear-gradient(90deg, #11998e, #38ef7d)"}, inverse=True,
                    className="shadow rounded p-3 mb-3"),

                html.Label("Powierzchnia dachu [m²]", className="fw-bold mt-2 mb-2"),
                dcc.Slider(
                    id='slider-roof-area',
                    min=25,
                    max=300,
                    step=1,
                    value=100,
                    marks={i: f"{i}" for i in range(25, 301, 25)},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], md=6, xs=12, className="mb-4")
        ])
    ])


def start_simulation_button():
    return dbc.Row([
        dbc.Col([

            html.Div(id="simulation-output", className="mt-3"),

            dbc.Button(
                "Potwierdź",
                id="simulate-button",
                color="success",
                className="w-100 rounded-pill shadow"
            ),

        ], width=3)
    ], justify="center", className="mt-4")


def simulation_graphs():
    return html.Div(id="water-graph")



def footer():
    return html.Footer("Inteligentne systemy sterowania 2025 | Michał Dwernicki, Jan Jóźwiak, Jakub Górski",
                       className="text-center text-muted mt-5 mb-3")


def toast_success_status(text):
    return dbc.Toast(
        id="simulation-toast",
        header="Sukces",
        icon="success",  # success, danger, warning, info, primary, secondary
        is_open=True,
        dismissable=True,
        duration=4000,  # automatyczne znikanie po 4000 ms (4 sekundy)
        children=text,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
    )

def toast_error_status(text):
    return dbc.Toast(
        id="simulation-toast",
        header="Błąd",
        icon="danger",  # success, danger, warning, info, primary, secondary
        is_open=True,
        dismissable=True,
        duration=4000,  # automatyczne znikanie po 4000 ms (4 sekundy)
        children=text,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
    )

def modal():
    return dbc.Modal(
    id="simulation-modal",
    is_open=False,
    size="xl",
    centered=True,
    children=[
        dbc.ModalHeader(dbc.ModalTitle("📈 Wynik Symulacji")),
        dbc.ModalBody(
            dcc.Graph(id="modal-graph", className="shadow rounded p-3 mb-3")
        ),
        dbc.ModalFooter(
            dbc.Button("Zamknij", id="close-modal", className="ms-auto", n_clicks=0)
        )
    ]
)


main_layout = dbc.Container([

    # Navbar
    navbar(),

    # Welcome section
    # welcome_section(),

    # Data section header
    data_section_header(),

    # Data section
    simulation_section(),

    # Simulation button
    start_simulation_button(),

    # Graph section
    simulation_graphs(),

    # Footer
    footer(),

], fluid=True, style={"padding": "0"})
