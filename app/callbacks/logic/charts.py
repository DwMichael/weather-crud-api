import plotly.express as px

color_map = {
    'Poziom wody [L]': 'blue',
    'Wpompowana woda [L]': 'green',
    'Zużyta woda [L]': 'red',
    'Zaoszczędzona woda [L]': '#00BFA9'
}

def generate_animation_chart(df, df_long):
    return px.bar(
        df_long,
        x='type',
        y='value',
        color='type',
        animation_frame=df_long['date'].dt.strftime('%Y-%m-%d'),
        title=f"Poziom wody - min: {df['water_amount'].min()}, max: {df['water_amount'].max()}",
        barmode="relative",
        labels={"value": "Objętość [L]", "type": "Rodzaj"},
        color_discrete_map=color_map,
    )

def generate_static_chart(df_long):
    return px.bar(
        df_long,
        x='date',
        y='value',
        color='type',
        title="Podsumowanie całego okresu",
        barmode="relative",
        labels={"value": "Objętość [L]", "date": "Data", "type": "Rodzaj"},
        color_discrete_map=color_map,
    )