from dash import Output, Input, State


def register_slider_callbacks(app):
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

    # Callback to update slider max value based on tank capacity
    @app.callback(
        Output("slider-min-level", "max"),
        Output("slider-min-level", "marks"),
        Output("slider-min-level", "value"),
        Input("slider-tank-capacity", "value"),
        State("slider-min-level", "value")
    )
    def update_min_slider_max(tank_capacity, current_min_value):
        # Rezerwa np. 100 L, żeby min level nie był równy pełnej pojemności
        new_max = max(1, tank_capacity - 100)

        # Oblicz ładne i równe marks
        marks = calculate_slider_marks(1, new_max)

        # Dopasuj wartość, jeśli przekracza nowy max
        new_value = min(current_min_value, new_max)

        return new_max, marks, new_value



def calculate_slider_marks(min_val, max_val, min_marks=2, max_marks=11):
    # Określenie możliwych kroków
    step = min(
        max_val // i for i in range(min_marks, max_marks) if max_val % i == 0
    )

    # Generuj wartości
    marks = {i: str(i) for i in range(min_val - 1, max_val + 1, step)}

    # Zawsze dodaj pierwszy i ostatni punkt jeśli ich brakuje
    if min_val not in marks:
        marks[min_val] = str(min_val)
    if max_val not in marks:
        marks[max_val] = str(max_val)

    return marks