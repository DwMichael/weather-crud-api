import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

color_map = {
    'Poziom wody [L]': 'blue',
    'Wpompowana woda [L]': 'green',
    'Zużyta woda [L]': 'red',
    'Zaoszczędzona woda [L]': '#00BFA9'
}

colors_pi = px.colors.qualitative.Plotly
colors_fuzzy = px.colors.qualitative.Dark24

color_map_sum = {
    "Regulator PI": "royalblue",
    "Regulator Rozmyty": "seagreen"
}

color_map_percentage = {
    "Regulator PI": "#9467bd",
    "Regulator Rozmyty": "#ffbb00"
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


def generate_static_chart(df_long, title="Podsumowanie całego okresu"):
    return px.bar(
        df_long,
        x='date',
        y='value',
        color='type',
        title=title,
        barmode="relative",
        labels={"value": "Objętość [L]", "date": "Data", "type": "Rodzaj"},
        color_discrete_map=color_map,
    )


def generate_comparison_subplots(df_pi_long, df_fuzzy_long):
    types = df_pi_long["type"].unique()
    n = len(types)
    cols = 2
    rows = math.ceil(n / cols)

    fig = make_subplots(
        rows=rows, cols=cols, shared_xaxes=True,
        subplot_titles=types
    )

    for i, t in enumerate(types):
        row = (i // cols) + 1
        col = (i % cols) + 1

        df_pi_filtered = df_pi_long[df_pi_long["type"] == t]
        df_fuzzy_filtered = df_fuzzy_long[df_fuzzy_long["type"] == t]

        color_pi = colors_pi[i % len(colors_pi)]
        color_fuzzy = colors_fuzzy[i % len(colors_fuzzy)]

        fig.add_trace(go.Scatter(
            x=df_pi_filtered["date"],
            y=df_pi_filtered["value"],
            mode="lines",
            name=f"PI - {t}",
            line=dict(color=color_pi, width=2)
        ), row=row, col=col)

        fig.add_trace(go.Scatter(
            x=df_fuzzy_filtered["date"],
            y=df_fuzzy_filtered["value"],
            mode="lines",
            name=f"Rozmyty - {t}",
            line=dict(color=color_fuzzy, width=2, dash="dash")
        ), row=row, col=col)

    fig.update_layout(
        height=300 * rows,
        title="Porównanie odpowiedzi regulatorów (podział na typy)",
        template="plotly_white",
        showlegend=True
    )
    return fig


def generate_total_comparison(df_pi_long, df_fuzzy_long):
    pi_total = df_pi_long.groupby("type")["value"].sum()
    fuzzy_total = df_fuzzy_long.groupby("type")["value"].sum()

    comparison_df = pd.DataFrame({
        "Rodzaj": pi_total.index,
        "Regulator PI": pi_total.values,
        "Regulator Rozmyty": fuzzy_total.values
    })

    comparison_df = comparison_df.melt(id_vars="Rodzaj", var_name="Regulator", value_name="Wartość")

    fig = px.bar(
        comparison_df,
        x="Rodzaj",
        y="Wartość",
        color="Regulator",
        barmode="group",
        color_discrete_map=color_map_sum,
        title="Porównanie sumaryczne regulatorów",
        labels={"Rodzaj": "Typ", "Wartość": "Suma [L]"}
    )

    return fig

def generate_average_comparison(df_pi_long, df_fuzzy_long):
    pi_avg = df_pi_long.groupby("type")["value"].mean()
    fuzzy_avg = df_fuzzy_long.groupby("type")["value"].mean()

    comparison_df = pd.DataFrame({
        "Rodzaj": pi_avg.index,
        "Regulator PI": pi_avg.values,
        "Regulator Rozmyty": fuzzy_avg.values
    })

    comparison_df = comparison_df.melt(id_vars="Rodzaj", var_name="Regulator", value_name="Wartość")

    fig = px.bar(
        comparison_df,
        x="Rodzaj",
        y="Wartość",
        color="Regulator",
        barmode="group",
        color_discrete_map=color_map_sum,
        title="Porównanie średniego poziomu wody",
        labels={"Rodzaj": "Typ", "Wartość": "Średnia [L]"}
    )

    return fig



def generate_percentage_comparison(df_pi_long, df_fuzzy_long):
    pi_total = df_pi_long.groupby("type")["value"].sum()
    fuzzy_total = df_fuzzy_long.groupby("type")["value"].sum()

    comparison_df = pd.DataFrame({
        "Rodzaj": pi_total.index,
        "Regulator PI": pi_total.values,
        "Regulator Rozmyty": fuzzy_total.values
    })

    # Zmiana struktury z szerokiej na długą
    comparison_df = comparison_df.melt(id_vars="Rodzaj", var_name="Regulator", value_name="Wartość")

    # Oblicz procentowy udział każdego regulatora w danej kategorii
    total_per_type = comparison_df.groupby("Rodzaj")["Wartość"].transform("sum")
    comparison_df["Procent"] = comparison_df["Wartość"] / total_per_type * 100

    # Tworzenie wykresu
    fig = px.bar(
        comparison_df,
        x="Rodzaj",
        y="Procent",
        color="Regulator",
        barmode="stack",
        color_discrete_map=color_map_percentage,
        title="Porównanie udziałów procentowych w każdej kategorii",
        labels={"Rodzaj": "Typ", "Procent": "Udział [%]"},
        text=round(comparison_df["Procent"], 1)
    )

    fig.update_traces(textposition='inside')
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    return fig


def generate_difference_chart(df_pi_long, df_fuzzy_long):
    pi_total = df_pi_long.groupby("type")["value"].sum()
    fuzzy_total = df_fuzzy_long.groupby("type")["value"].sum()

    diff = fuzzy_total - pi_total
    comparison_df = pd.DataFrame({
        "Rodzaj": diff.index,
        "Różnica": diff.values
    })

    fig = px.bar(
        comparison_df,
        x="Różnica",
        y="Rodzaj",
        orientation='h',
        color="Różnica",
        color_continuous_scale="RdYlGn",
        title="Różnica Fuzzy - PI dla każdej kategorii",
        labels={"Różnica": "Różnica [L]"}
    )
    return fig
