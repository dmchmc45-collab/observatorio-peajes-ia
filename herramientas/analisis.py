"""Cálculos determinísticos usados por el agente."""
import pandas as pd

def construir_ranking_peajes(datos, indicador="veh_total", cantidad=5):
    df = pd.DataFrame(datos)
    if df.empty:
        return []
    df[indicador] = pd.to_numeric(df[indicador], errors="coerce").fillna(0)
    resultado = (
        df.groupby(["nombre_peaje", "departamento"], as_index=False)[indicador]
        .sum()
        .sort_values(indicador, ascending=False)
        .head(int(cantidad))
    )
    return resultado.to_dict(orient="records")

def comparar_departamentos(datos, indicador="veh_total"):
    df = pd.DataFrame(datos)
    if df.empty:
        return []
    df[indicador] = pd.to_numeric(df[indicador], errors="coerce").fillna(0)
    resultado = (
        df.groupby("departamento", as_index=False)[indicador]
        .sum()
        .sort_values(indicador, ascending=False)
    )
    return resultado.to_dict(orient="records")

def composicion_vehicular(datos):
    df = pd.DataFrame(datos)
    if df.empty:
        return {}
    ligeros = pd.to_numeric(df["veh_ligeros_total"], errors="coerce").fillna(0).sum()
    pesados = pd.to_numeric(df["veh_pesados_total"], errors="coerce").fillna(0).sum()
    total = ligeros + pesados
    return {
        "veh_ligeros_total": int(ligeros),
        "veh_pesados_total": int(pesados),
        "veh_total_calculado": int(total),
        "pct_ligeros": round(ligeros / total * 100, 2) if total else 0,
        "pct_pesados": round(pesados / total * 100, 2) if total else 0,
    }
