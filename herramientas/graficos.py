"""Visualizaciones del proyecto."""
import pandas as pd
import plotly.express as px

def grafico_ranking(datos, indicador="veh_total"):
    df = pd.DataFrame(datos)
    if df.empty:
        return None
    return px.bar(
        df,
        x="nombre_peaje",
        y=indicador,
        title=f"Ranking de peajes por {indicador}",
        labels={"nombre_peaje": "Peaje", indicador: indicador},
    )
