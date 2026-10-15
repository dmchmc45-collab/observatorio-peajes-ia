import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

# Cargar conexión a Supabase
load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def ranking_peajes(anio: int, indicador: str = "VEH_TOTAL", cantidad: int = 5):
    """
    Obtiene el top de peajes con mayor flujo para un año específico.
    """
    respuesta = supabase.table("flujo_vehicular").select("NOMBRE_PEAJE", "DEPARTAMENTO", indicador).eq("ANIO", anio).execute()
    datos = respuesta.data
    
    if not datos:
        return {"error": f"No se encontraron datos para el año {anio}."}

    df = pd.DataFrame(datos)
    df[indicador] = pd.to_numeric(df[indicador], errors='coerce').fillna(0)
    df_agrupado = df.groupby(["NOMBRE_PEAJE", "DEPARTAMENTO"])[indicador].sum().reset_index()
    df_top = df_agrupado.sort_values(by=indicador, ascending=False).head(cantidad)
    
    return df_top.to_dict(orient="records")

def comparar_departamentos(anio: int, indicador: str = "VEH_TOTAL"):
    """
    Calcula el flujo vehicular total por departamento para un año específico.
    """
    respuesta = supabase.table("flujo_vehicular").select("DEPARTAMENTO", indicador).eq("ANIO", anio).execute()
    datos = respuesta.data
    
    if not datos:
        return {"error": f"No se encontraron datos para el año {anio}."}

    df = pd.DataFrame(datos)
    df[indicador] = pd.to_numeric(df[indicador], errors='coerce').fillna(0)
    df_agrupado = df.groupby("DEPARTAMENTO")[indicador].sum().reset_index()
    df_ordenado = df_agrupado.sort_values(by=indicador, ascending=False)
    
    return df_ordenado.to_dict(orient="records")

# --- BLOQUE DE PRUEBA LOCAL ---
if __name__ == "__main__":
    print("Probando comparar_departamentos para 2025...")
    resultado_dept = comparar_departamentos(anio=2025, indicador="VEH_TOTAL")
    
    # Mostrar solo el top 3 de departamentos
    for puesto, dept in enumerate(resultado_dept[:3], 1):
        print(f"{puesto}. {dept['DEPARTAMENTO']} - Flujo: {dept['VEH_TOTAL']:,.0f}")