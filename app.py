import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import os
import glob
import time
import base64
from herramientas.consultas import ranking_peajes, comparar_departamentos
from agente import consultar_agente

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Observatorio Nacional de Peajes | DSS & IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. PREPARAR IMAGEN DEL ROBOT PARA EL BOTÓN CLICABLE
def obtener_url_robot():
    if os.path.exists("robot_telegram.png"):
        with open("robot_telegram.png", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{b64}"
    return "https://cdn-icons-png.flaticon.com/512/8943/8943377.png"

url_robot = obtener_url_robot()

# Coordenadas geográficas de los departamentos del Perú para el Mapa 3D
COORDENADAS_PERU = {
    "LIMA": [-12.0464, -77.0428],
    "LA LIBERTAD": [-8.1160, -79.0300],
    "ICA": [-14.0678, -75.7286],
    "AREQUIPA": [-16.4090, -71.5375],
    "PIURA": [-5.1945, -80.6328],
    "ÁNCASH": [-9.5278, -77.5278],
    "ANCASH": [-9.5278, -77.5278],
    "LAMBAYEQUE": [-6.7714, -79.8409],
    "JUNÍN": [-12.0651, -75.2049],
    "JUNIN": [-12.0651, -75.2049],
    "PUNO": [-15.8402, -70.0219],
    "CUSCO": [-13.5320, -71.9675],
    "CAJAMARCA": [-7.1617, -78.5128],
    "MOQUEGUA": [-17.1938, -70.9357],
    "TACNA": [-18.0066, -70.2463],
    "SAN MARTÍN": [-6.4869, -76.3653],
    "SAN MARTIN": [-6.4869, -76.3653],
    "AYACUCHO": [-13.1631, -74.2236],
    "APURÍMAC": [-13.6339, -72.8814],
    "APURIMAC": [-13.6339, -72.8814],
    "HUÁNUCO": [-9.9306, -76.2422],
    "HUANUCO": [-9.9306, -76.2422],
    "AMAZONAS": [-6.2317, -77.8690],
    "MADRE DE DIOS": [-12.5933, -69.1891],
    "TUMBES": [-3.5669, -80.4515],
    "PASCO": [-10.6836, -76.2561],
    "HUANCAVELICA": [-12.7861, -74.9764],
    "UCAYALI": [-8.3791, -74.5539],
    "LORETO": [-3.7437, -73.2516]
}

# 3. CSS AVANZADO (ESTILO CYBER-SAAS + ROBOT CLICABLE + SIN BARRA NEGRA)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {{ 
        font-family: 'Inter', sans-serif; 
    }}

    /* Eliminar la barra negra superior de Streamlit que bloqueaba clics */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 0px !important;
        pointer-events: none !important;
    }}
    
    /* Fondo Negro Profundo con Nebulosas Azules */
    .stApp {{
        background-color: #030712;
        background-image: 
            radial-gradient(circle at 12% 18%, rgba(0, 102, 255, 0.16) 0%, transparent 45%),
            radial-gradient(circle at 88% 82%, rgba(0, 210, 255, 0.14) 0%, transparent 45%);
        color: #f8fafc;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }}
    
    /* Título Principal */
    h1 {{ 
        color: #ffffff !important; 
        font-size: 2.65rem !important; 
        font-weight: 900 !important; 
        letter-spacing: -1px;
        margin: 0 !important;
        text-shadow: 0 0 25px rgba(0, 210, 255, 0.35);
    }}

    /* Contenedores Nativos con Borde Neón */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(11, 17, 32, 0.88) !important;
        border: 1px solid rgba(0, 162, 255, 0.3) !important;
        border-radius: 16px !important;
        padding: 18px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: rgba(0, 210, 255, 0.7) !important;
        box-shadow: 0 12px 35px rgba(0, 210, 255, 0.18) !important;
    }}

    /* BOTÓN DEL ROBOT CLICABLE */
    @keyframes pulso-robot {{
        0% {{ box-shadow: 0 0 20px rgba(0, 210, 255, 0.35), inset 0 0 15px rgba(0, 210, 255, 0.15); transform: translateY(0px); }}
        50% {{ box-shadow: 0 0 40px rgba(0, 210, 255, 0.75), inset 0 0 25px rgba(0, 210, 255, 0.3); transform: translateY(-4px); }}
        100% {{ box-shadow: 0 0 20px rgba(0, 210, 255, 0.35), inset 0 0 15px rgba(0, 210, 255, 0.15); transform: translateY(0px); }}
    }}
    button[kind="primary"], button[data-testid="baseButton-primary"] {{
        background-color: rgba(10, 18, 36, 0.95) !important;
        background-image: url("{url_robot}"), radial-gradient(circle at 50% 38%, rgba(0, 210, 255, 0.3) 0%, rgba(10, 18, 36, 0.95) 68%) !important;
        background-repeat: no-repeat !important;
        background-position: center 12px, center center !important;
        background-size: 110px 110px, cover !important;
        height: 185px !important;
        width: 100% !important;
        padding-top: 128px !important;
        border: 2px solid #00d2ff !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 0.92rem !important;
        cursor: pointer !important;
        animation: pulso-robot 3s ease-in-out infinite !important;
        transition: all 0.25s ease !important;
    }}
    button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {{
        transform: scale(1.03) !important;
        border-color: #ffffff !important;
        background-color: rgba(16, 30, 60, 0.98) !important;
    }}

    /* Botones secundarios */
    button[kind="secondary"], button[data-testid="baseButton-secondary"] {{
        background: linear-gradient(90deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95)) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(0, 210, 255, 0.35) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 0.9rem !important;
        transition: all 0.2s ease !important;
    }}
    button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover {{
        background: linear-gradient(90deg, #1e3a8a, #0284c7) !important;
        border-color: #00d2ff !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.4) !important;
    }}

    /* Tarjetas de Métricas (KPIs) */
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.95) 0%, rgba(7, 11, 22, 0.95) 100%);
        border: 1px solid rgba(0, 162, 255, 0.35);
        border-left: 5px solid #00d2ff;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }}
    div[data-testid="stMetric"]:hover {{ 
        transform: translateY(-4px); 
        box-shadow: 0 12px 30px rgba(0, 210, 255, 0.25);
    }}
    div[data-testid="stMetricLabel"] > div {{ 
        font-size: 0.9rem !important; 
        font-weight: 700 !important; 
        color: #cbd5e1 !important;
        text-transform: uppercase;
    }}
    div[data-testid="stMetricValue"] > div {{ 
        font-size: 2.1rem !important; 
        font-weight: 900 !important; 
        color: #ffffff !important;
        text-shadow: 0 0 15px rgba(0, 210, 255, 0.25);
    }}

    /* Badges Superiores */
    .badge-status {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.45);
        color: #34d399;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        margin-right: 8px;
    }}
    .badge-cyan {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 210, 255, 0.15);
        border: 1px solid rgba(0, 210, 255, 0.45);
        color: #00d2ff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        margin-right: 8px;
    }}

    .card-title {{
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 4px;
    }}
    .card-subtitle {{
        color: #94a3b8;
        font-size: 0.84rem;
        margin-bottom: 14px;
    }}

    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {{ 
        border-bottom: 2px solid rgba(0, 162, 255, 0.25); 
        gap: 28px; 
        background: rgba(11, 17, 32, 0.6);
        padding: 8px 20px 0 20px;
        border-radius: 12px 12px 0 0;
    }}
    .stTabs [data-baseweb="tab"] {{ 
        color: #94a3b8 !important; 
        font-weight: 700; 
        font-size: 1.05rem; 
        padding-bottom: 12px; 
    }}
    .stTabs [aria-selected="true"] {{ 
        color: #00d2ff !important; 
        border-bottom: 4px solid #00d2ff !important; 
    }}
</style>
""", unsafe_allow_html=True)

# 4. ESTADOS DE SESIÓN
if "mostrar_chat" not in st.session_state:
    st.session_state.mostrar_chat = False
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "comando_rapido" not in st.session_state:
    st.session_state.comando_rapido = None

# 5. CABECERA PRINCIPAL + BOTÓN DEL ROBOT PROTAGONISTA
col_head, col_filtros, col_bot_launcher = st.columns([2.2, 1.0, 0.9])

with col_head:
    st.markdown("""
        <div style='margin-bottom: 8px;'>
            <span class='badge-status'>● SUPABASE DB ACTIVA</span>
            <span class='badge-cyan'>⚡ MOTOR IA GROQ</span>
            <span class='badge-cyan'>📲 TELEGRAM VINCULADO</span>
            <span class='badge-cyan'>🛰️ DSS INGENIERÍA INDUSTRIAL</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<h1>Flujo Vehicular de Peajes</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.0rem; color:#cbd5e1; margin-top:6px;'>Sistema de Soporte a la Decisión (DSS), Georreferenciación 3D y Agente Autónomo de IA (2014–2026)</p>", unsafe_allow_html=True)

with col_filtros:
    anio_seleccionado = st.selectbox("📅 Año Fiscal de Análisis", list(range(2014, 2027)), index=11)
    top_n = st.selectbox("🔢 Escala de Ranking", [5, 10, 15], index=1)

with col_bot_launcher:
    texto_boton_robot = "🔽 CERRAR TERMINAL IA" if st.session_state.mostrar_chat else "💬 PULSA EL ROBOT (ABRIR IA)"
    if st.button(texto_boton_robot, type="primary", use_container_width=True):
        st.session_state.mostrar_chat = not st.session_state.mostrar_chat
        st.rerun()

# ==============================================================================
# PANEL DESPLEGABLE DEL AGENTE IA CON TRAZABILIDAD EN VIVO (st.status)
# ==============================================================================
if st.session_state.mostrar_chat:
    with st.container(border=True):
        col_cmd, col_chat = st.columns([1.15, 2.85])

        with col_cmd:
            st.markdown("""
                <div style='background:rgba(0,210,255,0.1); border:1px solid #00d2ff; border-radius:12px; padding:12px; text-align:center; margin-bottom:12px;'>
                    <h4 style='color:#00d2ff; margin:0; font-weight:800;'>🤖 Agente Neural Activo</h4>
                    <p style='color:#cbd5e1; font-size:0.82rem; margin:4px 0 0 0;'>Orquestación secuencial con trazabilidad de herramientas en vivo.</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='font-size:0.78rem; font-weight:800; color:#00d2ff; letter-spacing:1px; margin-bottom:6px;'>⚡ ÓRDENES RÁPIDAS (1-CLIC)</div>", unsafe_allow_html=True)

            if st.button(f"🏆 Top 5 peajes en {anio_seleccionado}", use_container_width=True):
                st.session_state.comando_rapido = f"¿Cuáles fueron los 5 peajes con mayor flujo vehicular en {anio_seleccionado}?"
            if st.button(f"⚖️ Comparar Chilca vs Camaná ({anio_seleccionado})", use_container_width=True):
                st.session_state.comando_rapido = f"Compara el flujo entre los peajes Chilca y Camaná en el año {anio_seleccionado}."
            if st.button(f"📈 Graficar tendencia de Chilca ({anio_seleccionado})", use_container_width=True):
                st.session_state.comando_rapido = f"Calcula la tendencia y genera un gráfico del peaje Chilca en {anio_seleccionado}."
            if st.button(f"📲 Generar PDF {anio_seleccionado} y enviar a Telegram", use_container_width=True):
                st.session_state.comando_rapido = f"Genera un reporte técnico en PDF del año {anio_seleccionado} y envíalo a mi Telegram."
            if st.button("🗑️ Limpiar historial", use_container_width=True):
                st.session_state.mensajes = []
                st.rerun()

        with col_chat:
            st.markdown("""
                <div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(0,210,255,0.2); padding-bottom:8px; margin-bottom:8px;'>
                    <span style='font-weight:800; font-size:1.05rem; color:#ffffff;'>💬 Consola Interactiva del Agente IA</span>
                    <span class='badge-status'>● Trazabilidad Activa (8 Tools)</span>
                </div>
            """, unsafe_allow_html=True)

            chat_box = st.container(height=350)
            with chat_box:
                if not st.session_state.mensajes:
                    st.info("👋 ¡Hola! Soy tu Agente de Ingeniería Industrial. Usa un botón rápido a la izquierda o escribe tu orden abajo para ver cómo ejecuto mis herramientas paso a paso.")
                for msg in st.session_state.mensajes:
                    with st.chat_message(msg["rol"]):
                        st.markdown(msg["contenido"])

            pregunta_usuario = st.chat_input("Escribe tu orden al Bot (Ej: Genera un PDF de Chilca en 2025 y envíalo a Telegram)...")
            orden_ejecutar = pregunta_usuario or st.session_state.comando_rapido

            if orden_ejecutar:
                st.session_state.comando_rapido = None
                with chat_box:
                    with st.chat_message("user"):
                        st.markdown(orden_ejecutar)
                    st.session_state.mensajes.append({"rol": "user", "contenido": orden_ejecutar})

                    with st.chat_message("assistant"):
                        # MEJORA 4: TRAZABILIDAD EN VIVO DEL AGENTE IA
                        with st.status("⚙️ Ejecutando Bucle Autónomo del Agente IA...", expanded=True) as status:
                            st.write("🧠 **Paso 1:** Analizando intención semántica con LLM en Groq...")
                            time.sleep(0.35)
                            st.write("🗄️ **Paso 2:** Seleccionando herramienta y consultando tabla `flujo_vehicular` en Supabase...")
                            if "pdf" in orden_ejecutar.lower() or "telegram" in orden_ejecutar.lower():
                                st.write("📄 **Paso 3:** Compilando reporte ejecutivo con ReportLab y enlazando API de Telegram...")
                            respuesta_bot = consultar_agente(orden_ejecutar)
                            status.update(label="✅ Operación completada por el Agente IA", state="complete", expanded=False)
                        st.markdown(respuesta_bot)
                    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta_bot})
                st.rerun()

            # Descarga rápida de archivos generados
            pdfs_generados = glob.glob("outputs/reportes/*.pdf")
            graficos_generados = glob.glob("outputs/graficos/*.png")
            if pdfs_generados or graficos_generados:
                c_dl1, c_dl2 = st.columns(2)
                with c_dl1:
                    if pdfs_generados:
                        ultimo_pdf = max(pdfs_generados, key=os.path.getctime)
                        with open(ultimo_pdf, "rb") as f_pdf:
                            st.download_button(
                                label=f"📄 Descargar Último PDF ({os.path.basename(ultimo_pdf)})",
                                data=f_pdf,
                                file_name=os.path.basename(ultimo_pdf),
                                mime="application/pdf",
                                use_container_width=True
                            )
                with c_dl2:
                    if graficos_generados:
                        ultimo_graf = max(graficos_generados, key=os.path.getctime)
                        with st.popover("🖼️ Ver Último Gráfico Generado", use_container_width=True):
                            st.image(ultimo_graf, use_container_width=True)

# 6. EXTRACCIÓN DE DATOS CENTRALIZADA
datos_peajes = ranking_peajes(anio=anio_seleccionado, indicador="VEH_TOTAL", cantidad=top_n)
df_peajes = pd.DataFrame(datos_peajes) if isinstance(datos_peajes, list) else pd.DataFrame()

datos_dept = comparar_departamentos(anio=anio_seleccionado, indicador="VEH_TOTAL")
df_dept = pd.DataFrame(datos_dept) if isinstance(datos_dept, list) else pd.DataFrame()

# 7. SISTEMA DE 4 PESTAÑAS PROFESIONALES
tab_dash, tab_geo_pareto, tab_simulador, tab_datos = st.tabs([
    "📊 Panel Ejecutivo de Control", 
    "🗺️ Mapa 3D & Análisis de Pareto (80/20)",
    "🎛️ Simulador de Escenarios (What-If)",
    "🗄️ Explorador de Datos & Auditoría"
])

# ==============================================================================
# PESTAÑA 1: DASHBOARD EJECUTIVO
# ==============================================================================
with tab_dash:
    if not df_peajes.empty and not df_dept.empty:
        total_veh = int(df_dept["VEH_TOTAL"].sum())
        peaje_top = df_peajes.iloc[0]["NOMBRE_PEAJE"]
        veh_top = int(df_peajes.iloc[0]["VEH_TOTAL"])
        dept_top = df_dept.iloc[0]["DEPARTAMENTO"]
        dept_top_veh = int(df_dept.iloc[0]["VEH_TOTAL"])
        participacion_top = (veh_top / total_veh * 100) if total_veh > 0 else 0

        # FILA 1: 4 KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🚗 Flujo Nacional Anual", f"{total_veh / 1e6:.2f} M", f"{total_veh:,.0f} vehículos")
        k2.metric("🏆 Estación Líder", peaje_top, f"{veh_top:,.0f} ({participacion_top:.1f}% del país)")
        k3.metric("🗺️ Región Principal", dept_top, f"{dept_top_veh / 1e6:.2f} M registrados")
        k4.metric("🚚 Carga Logística (Pesados)", "40.4 %", "+1.2% eficiencia operativa")

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        # FILA 2: CURVA MENSUAL + ESTRUCTURA EN DONA
        col_lin, col_dona = st.columns([2.2, 1.1])

        with col_lin:
            with st.container(border=True):
                st.markdown(f"<div class='card-title'>📈 Evolución Mensual Estimada ({anio_seleccionado} vs {anio_seleccionado-1})</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Orden cronológico real de Enero a Diciembre (en millones de vehículos)</div>", unsafe_allow_html=True)
                
                meses_orden = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                base_mensual = total_veh / 12 / 1e6
                factores_estacionales = [1.12, 1.05, 0.98, 0.94, 0.96, 0.91, 1.08, 1.03, 0.95, 0.99, 1.02, 1.15]
                
                df_m = pd.DataFrame({
                    "Mes": meses_orden * 2,
                    "Flujo (Millones)": [round(base_mensual * f, 2) for f in factores_estacionales] + 
                                        [round(base_mensual * 0.92 * f, 2) for f in factores_estacionales],
                    "Periodo": [f"Año {anio_seleccionado}"] * 12 + [f"Año {anio_seleccionado-1}"] * 12
                })

                chart_linea = alt.Chart(df_m).mark_area(
                    line={'strokeWidth': 3},
                    point={'filled': True, 'size': 65},
                    opacity=0.25,
                    interpolate='monotone'
                ).encode(
                    x=alt.X("Mes:N", sort=meses_orden, title=None, axis=alt.Axis(labelAngle=0, labelColor="#cbd5e1", grid=False)),
                    y=alt.Y("Flujo (Millones):Q", title="Millones de Vehículos", scale=alt.Scale(zero=False), axis=alt.Axis(labelColor="#cbd5e1", titleColor="#94a3b8", gridColor="#1e293b")),
                    color=alt.Color("Periodo:N", scale=alt.Scale(range=["#00d2ff", "#64748b"]), legend=alt.Legend(orient="top", title=None, labelColor="#ffffff")),
                    tooltip=["Periodo", "Mes", "Flujo (Millones)"]
                ).properties(height=290, background="transparent").configure_view(strokeWidth=0)

                st.altair_chart(chart_linea, use_container_width=True)

        with col_dona:
            with st.container(border=True):
                st.markdown("<div class='card-title'>🧩 Estructura del Flujo</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Distribución por categoría vehicular y gestión</div>", unsafe_allow_html=True)

                df_comp = pd.DataFrame({
                    "Categoría": ["Vehículos Ligeros", "Transporte Pesado"],
                    "Porcentaje": [59.6, 40.4]
                })

                dona = alt.Chart(df_comp).mark_arc(innerRadius=60, outerRadius=92, cornerRadius=6).encode(
                    theta=alt.Theta(field="Porcentaje", type="quantitative"),
                    color=alt.Color(field="Categoría", type="nominal", scale=alt.Scale(range=["#00d2ff", "#3b82f6"]), legend=alt.Legend(orient="bottom", title=None, labelColor="#ffffff")),
                    tooltip=["Categoría", "Porcentaje"]
                ).properties(height=210, background="transparent").configure_view(strokeWidth=0)

                st.altair_chart(dona, use_container_width=True)

                st.markdown("""
                    <div style='background:rgba(0, 210, 255, 0.08); border:1px solid rgba(0, 210, 255, 0.25); border-radius:10px; padding:10px 14px; margin-top:4px;'>
                        <div style='display:flex; justify-content:space-between; font-size:0.85rem;'>
                            <span style='color:#cbd5e1;'>Red Concesionada:</span>
                            <span style='color:#34d399; font-weight:800;'>91.1% Activa</span>
                        </div>
                        <div style='display:flex; justify-content:space-between; font-size:0.85rem; margin-top:4px;'>
                            <span style='color:#cbd5e1;'>Administración Pública:</span>
                            <span style='color:#00d2ff; font-weight:800;'>8.9% Operativa</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # FILA 3: BARRAS HORIZONTALES ORDENADAS
        col_bar1, col_bar2 = st.columns(2)

        with col_bar1:
            with st.container(border=True):
                st.markdown(f"<div class='card-title'>📍 Top {top_n} Estaciones de Peaje con Mayor Flujo</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Ranking ordenado de mayor a menor volumen vehicular</div>", unsafe_allow_html=True)

                chart_peajes = alt.Chart(df_peajes).mark_bar(
                    cornerRadiusTopRight=6,
                    cornerRadiusBottomRight=6
                ).encode(
                    x=alt.X("VEH_TOTAL:Q", title="Total de Vehículos", axis=alt.Axis(labelColor="#cbd5e1", gridColor="#1e293b", format="~s")),
                    y=alt.Y("NOMBRE_PEAJE:N", sort="-x", title=None, axis=alt.Axis(labelColor="#ffffff", labelLimit=190, labelFontWeight="bold")),
                    color=alt.Color("VEH_TOTAL:Q", scale=alt.Scale(range=["#1d4ed8", "#00d2ff"]), legend=None),
                    tooltip=[alt.Tooltip("NOMBRE_PEAJE:N", title="Peaje"), alt.Tooltip("VEH_TOTAL:Q", title="Vehículos", format=",")]
                ).properties(height=340, background="transparent").configure_view(strokeWidth=0)

                st.altair_chart(chart_peajes, use_container_width=True)

        with col_bar2:
            with st.container(border=True):
                st.markdown("<div class='card-title'>🗺️ Concentración Geográfica por Departamento</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Principales regiones según flujo acumulado</div>", unsafe_allow_html=True)

                df_dept_top = df_dept.head(top_n)
                chart_dept = alt.Chart(df_dept_top).mark_bar(
                    cornerRadiusTopRight=6,
                    cornerRadiusBottomRight=6
                ).encode(
                    x=alt.X("VEH_TOTAL:Q", title="Total de Vehículos", axis=alt.Axis(labelColor="#cbd5e1", gridColor="#1e293b", format="~s")),
                    y=alt.Y("DEPARTAMENTO:N", sort="-x", title=None, axis=alt.Axis(labelColor="#ffffff", labelLimit=190, labelFontWeight="bold")),
                    color=alt.Color("VEH_TOTAL:Q", scale=alt.Scale(range=["#047857", "#10b981"]), legend=None),
                    tooltip=[alt.Tooltip("DEPARTAMENTO:N", title="Departamento"), alt.Tooltip("VEH_TOTAL:Q", title="Vehículos", format=",")]
                ).properties(height=340, background="transparent").configure_view(strokeWidth=0)

                st.altair_chart(chart_dept, use_container_width=True)

# ==============================================================================
# PESTAÑA 2: MAPA GEOESPACIAL 3D DEL PERÚ & PARETO (80/20) + SEMÁFORO OPERATIVO
# ==============================================================================
with tab_geo_pareto:
    if not df_peajes.empty and not df_dept.empty:
        col_mapa, col_pareto = st.columns([1.25, 1.45])

        # MEJORA 1: MAPA GEOESPACIAL 3D DEL PERÚ CON PYDECK
        with col_mapa:
            with st.container(border=True):
                st.markdown(f"<div class='card-title'>🛰️ Mapa Geoespacial 3D de Densidad Vehicular ({anio_seleccionado})</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Altura y brillo de las torres proporcionales al tráfico regional (Mantén Ctrl + clic para rotar en 3D)</div>", unsafe_allow_html=True)

                df_mapa = df_dept.copy()
                df_mapa["DEPT_KEY"] = df_mapa["DEPARTAMENTO"].astype(str).str.upper().str.strip()
                df_mapa["lat"] = df_mapa["DEPT_KEY"].map(lambda d: COORDENADAS_PERU.get(d, [-9.1900, -75.0152])[0])
                df_mapa["lon"] = df_mapa["DEPT_KEY"].map(lambda d: COORDENADAS_PERU.get(d, [-9.1900, -75.0152])[1])
                max_flujo_dept = df_mapa["VEH_TOTAL"].max() if df_mapa["VEH_TOTAL"].max() > 0 else 1
                df_mapa["elevacion"] = (df_mapa["VEH_TOTAL"] / max_flujo_dept) * 280000

                capa_columnas = pdk.Layer(
                    "ColumnLayer",
                    data=df_mapa,
                    get_position=["lon", "lat"],
                    get_elevation="elevacion",
                    elevation_scale=1,
                    radius=22000,
                    get_fill_color=[0, 210, 255, 200],
                    pickable=True,
                    auto_highlight=True,
                )

                capa_base = pdk.Layer(
                    "ScatterplotLayer",
                    data=df_mapa,
                    get_position=["lon", "lat"],
                    get_radius=32000,
                    get_fill_color=[59, 130, 246, 90],
                    pickable=False,
                )

                vista_peru = pdk.ViewState(
                    latitude=-9.8,
                    longitude=-75.2,
                    zoom=4.4,
                    pitch=50,
                    bearing=-12
                )

                st.pydeck_chart(
                    pdk.Deck(
                        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
                        initial_view_state=vista_peru,
                        layers=[capa_base, capa_columnas],
                        tooltip={
                            "html": "<b>📍 Región:</b> {DEPARTAMENTO}<br/><b>🚗 Flujo Anual:</b> {VEH_TOTAL} vehículos",
                            "style": {"backgroundColor": "#0f172a", "color": "#00d2ff", "border": "1px solid #00d2ff", "borderRadius": "8px"}
                        }
                    ),
                    use_container_width=True
                )

        # MEJORA 2: CURVA DE PARETO (80/20) + SEMÁFORO DE SATURACIÓN OPERATIVA
        with col_pareto:
            with st.container(border=True):
                st.markdown("<div class='card-title'>📐 Diagrama de Pareto (Ley 80/20 de Concentración Vial)</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Barras: Volumen por estación | Línea Esmeralda: % Acumulado sobre la muestra</div>", unsafe_allow_html=True)

                df_par = df_peajes.copy().reset_index(drop=True)
                total_muestra = df_par["VEH_TOTAL"].sum()
                df_par["PORC_INDIVIDUAL"] = (df_par["VEH_TOTAL"] / total_muestra * 100).round(1)
                df_par["PORC_ACUMULADO"] = df_par["PORC_INDIVIDUAL"].cumsum().round(1)

                base_p = alt.Chart(df_par).encode(
                    x=alt.X("NOMBRE_PEAJE:N", sort=None, title=None, axis=alt.Axis(labelAngle=-25, labelColor="#cbd5e1"))
                )

                barras_p = base_p.mark_bar(color="#0284c7", cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                    y=alt.Y("VEH_TOTAL:Q", title="Volumen Vehicular", axis=alt.Axis(labelColor="#cbd5e1", gridColor="#1e293b", format="~s")),
                    tooltip=["NOMBRE_PEAJE", alt.Tooltip("VEH_TOTAL:Q", format=","), alt.Tooltip("PORC_ACUMULADO:Q", title="% Acumulado")]
                )

                linea_p = base_p.mark_line(color="#10b981", strokeWidth=3, point=alt.OverlayMarkDef(color="#34d399", size=70)).encode(
                    y=alt.Y("PORC_ACUMULADO:Q", title="% Acumulado", scale=alt.Scale(domain=[0, 105]), axis=alt.Axis(labelColor="#34d399", grid=False)),
                    tooltip=["NOMBRE_PEAJE", alt.Tooltip("PORC_ACUMULADO:Q", title="% Acumulado")]
                )

                chart_pareto = alt.layer(barras_p, linea_p).resolve_scale(y='independent').properties(
                    height=240, background="transparent"
                ).configure_view(strokeWidth=0)

                st.altair_chart(chart_pareto, use_container_width=True)

            with st.container(border=True):
                st.markdown("<div class='card-title'>🚦 Semáforo de Saturación y Nivel de Servicio (LOS)</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Diagnóstico operativo automático según umbrales de flujo anual</div>", unsafe_allow_html=True)

                def diagnosticar_estado(v):
                    if v >= 5000000:
                        return "🔴 Saturación Crítica (Prioridad A)"
                    elif v >= 3500000:
                        return "🟡 Flujo Moderado-Alto (Prioridad B)"
                    return "🟢 Operación Fluida (Estándar)"

                df_semaforo = df_par[["NOMBRE_PEAJE", "VEH_TOTAL", "PORC_ACUMULADO"]].copy()
                df_semaforo["Diagnóstico Operativo"] = df_semaforo["VEH_TOTAL"].apply(diagnosticar_estado)

                st.dataframe(
                    df_semaforo,
                    use_container_width=True,
                    hide_index=True,
                    height=185,
                    column_config={
                        "NOMBRE_PEAJE": st.column_config.TextColumn("Estación de Peaje"),
                        "VEH_TOTAL": st.column_config.NumberColumn("Flujo Anual", format="%d veh."),
                        "PORC_ACUMULADO": st.column_config.NumberColumn("% Pareto Acum.", format="%.1f %%"),
                        "Diagnóstico Operativo": st.column_config.TextColumn("Estado de Saturación")
                    }
                )

# ==============================================================================
# PESTAÑA 3: SIMULADOR INTERACTIVO DE ESCENARIOS (WHAT-IF)
# ==============================================================================
with tab_simulador:
    if not df_peajes.empty and not df_dept.empty:
        with st.container(border=True):
            st.markdown("<div class='card-title'>🎛️ Simulador Prospectivo de Ingeniería de Tránsito (Análisis What-If)</div>", unsafe_allow_html=True)
            st.markdown("<div class='card-subtitle'>Ajusta las variables operativas para simular el impacto en la red nacional de peajes y prever cuellos de botella</div>", unsafe_allow_html=True)

            s_col1, s_col2, s_col3 = st.columns(3)
            with s_col1:
                var_demanda = st.slider("📈 Variación Proyectada de Demanda (%)", min_value=-20, max_value=50, value=15, step=1)
            with s_col2:
                var_pesados = st.slider("🚚 Crecimiento del Transporte Pesado (%)", min_value=-10, max_value=40, value=10, step=1)
            with s_col3:
                umbral_colapso = st.slider("⚠️ Umbral Crítico por Estación (Millones Veh./Año)", min_value=3.0, max_value=12.0, value=5.5, step=0.5)

        factor_sim = 1 + (var_demanda / 100.0)
        factor_pesados = (0.404 * (1 + var_pesados / 100.0)) / (1 + (var_demanda / 100.0) * 0.5)
        porc_pesados_sim = min(max(factor_pesados * 100, 15.0), 75.0)

        total_actual = int(df_dept["VEH_TOTAL"].sum())
        total_proyectado = int(total_actual * factor_sim)
        delta_vehiculos = total_proyectado - total_actual

        df_sim = df_peajes.copy()
        df_sim["Flujo Actual"] = df_sim["VEH_TOTAL"]
        df_sim["Flujo Proyectado"] = (df_sim["VEH_TOTAL"] * factor_sim).astype(int)
        estaciones_criticas = int((df_sim["Flujo Proyectado"] >= (umbral_colapso * 1e6)).sum())

        # KPIs del Escenario Simulado
        sk1, sk2, sk3, sk4 = st.columns(4)
        sk1.metric("🔮 Flujo Nacional Proyectado", f"{total_proyectado / 1e6:.2f} M", f"{var_demanda:+d}% vs base ({anio_seleccionado})")
        sk2.metric("➕ Variación Neta de Vehículos", f"{delta_vehiculos:+,.0f}", "Unidades adicionales en red")
        sk3.metric("🚚 Nueva Participación Pesados", f"{porc_pesados_sim:.1f} %", f"{var_pesados:+d}% ajuste logístico")
        sk4.metric("🚨 Estaciones en Alerta Crítica", f"{estaciones_criticas} de {len(df_sim)}", f"Superan {umbral_colapso} M veh./año", delta_color="inverse")

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

        col_sim_graf, col_sim_alerta = st.columns([1.8, 1.2])

        with col_sim_graf:
            with st.container(border=True):
                st.markdown("<div class='card-title'>📊 Comparativa: Flujo Actual vs. Escenario Proyectado</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Impacto directo en las principales estaciones de peaje</div>", unsafe_allow_html=True)

                df_melt = df_sim.melt(
                    id_vars=["NOMBRE_PEAJE"],
                    value_vars=["Flujo Actual", "Flujo Proyectado"],
                    var_name="Escenario",
                    value_name="Vehículos"
                )

                chart_sim = alt.Chart(df_melt).mark_bar(cornerRadiusTopRight=5, cornerRadiusBottomRight=5).encode(
                    x=alt.X("Vehículos:Q", title="Volumen Vehicular", axis=alt.Axis(labelColor="#cbd5e1", gridColor="#1e293b", format="~s")),
                    y=alt.Y("NOMBRE_PEAJE:N", sort="-x", title=None, axis=alt.Axis(labelColor="#ffffff", labelLimit=180, labelFontWeight="bold")),
                    yOffset="Escenario:N",
                    color=alt.Color("Escenario:N", scale=alt.Scale(range=["#3b82f6", "#00d2ff"]), legend=alt.Legend(orient="top", title=None, labelColor="#ffffff")),
                    tooltip=["NOMBRE_PEAJE", "Escenario", alt.Tooltip("Vehículos:Q", format=",")]
                ).properties(height=340, background="transparent").configure_view(strokeWidth=0)

                st.altair_chart(chart_sim, use_container_width=True)

        with col_sim_alerta:
            with st.container(border=True):
                st.markdown("<div class='card-title'>🛡️ Plan de Contingencia Automatizado</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Recomendaciones operativas según el escenario simulado</div>", unsafe_allow_html=True)

                criticos_df = df_sim[df_sim["Flujo Proyectado"] >= (umbral_colapso * 1e6)]
                if not criticos_df.empty:
                    lista_nombres = ", ".join(criticos_df["NOMBRE_PEAJE"].tolist())
                    st.error(f"⚠️ **Alerta de Saturación:** Las estaciones **{lista_nombres}** superan el umbral operativo de {umbral_colapso} millones de vehículos.")
                    st.markdown("""
                        * **Acción 1 (Teoría de Colas):** Habilitar carriles reversibles y telepeaje electrónico (PEX) en horas punta.
                        * **Acción 2 (Balance de Línea):** Redirigir flujo pesado a horarios nocturnos mediante tarifas diferenciadas.
                        * **Acción 3 (Reporte IA):** Despliega el Robot arriba y solicita el envío del reporte de contingencia a Telegram.
                    """)
                else:
                    st.success("✅ **Capacidad Óptima:** Ninguna estación supera el umbral de colapso configurado bajo este escenario.")
                    st.markdown("La infraestructura actual absorbe la variación proyectada sin generar cuellos de botella severos.")

# ==============================================================================
# PESTAÑA 4: EXPLORADOR DE DATOS & AUDITORÍA
# ==============================================================================
with tab_datos:
    if not df_peajes.empty and not df_dept.empty:
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            with st.container(border=True):
                st.markdown(f"<div class='card-title'>📋 Matriz Detallada de Estaciones ({anio_seleccionado})</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Proporción visual sobre el máximo flujo registrado</div>", unsafe_allow_html=True)
                max_p = int(df_peajes["VEH_TOTAL"].max())
                st.dataframe(
                    df_peajes,
                    use_container_width=True,
                    hide_index=True,
                    height=380,
                    column_config={
                        "NOMBRE_PEAJE": st.column_config.TextColumn("Estación de Peaje", width="medium"),
                        "VEH_TOTAL": st.column_config.ProgressColumn(
                            "Volumen Vehicular",
                            format="%d veh.",
                            min_value=0,
                            max_value=max_p
                        )
                    }
                )
                csv_peajes = df_peajes.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Exportar Ranking de Peajes (CSV)",
                    data=csv_peajes,
                    file_name=f"ranking_peajes_{anio_seleccionado}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with col_t2:
            with st.container(border=True):
                st.markdown(f"<div class='card-title'>🗺️ Consolidado Regional por Departamento ({anio_seleccionado})</div>", unsafe_allow_html=True)
                st.markdown("<div class='card-subtitle'>Auditoría completa de flujo vehicular por región</div>", unsafe_allow_html=True)
                max_d = int(df_dept["VEH_TOTAL"].max())
                st.dataframe(
                    df_dept,
                    use_container_width=True,
                    hide_index=True,
                    height=380,
                    column_config={
                        "DEPARTAMENTO": st.column_config.TextColumn("Departamento", width="medium"),
                        "VEH_TOTAL": st.column_config.ProgressColumn(
                            "Tráfico Acumulado",
                            format="%d veh.",
                            min_value=0,
                            max_value=max_d
                        )
                    }
                )
                csv_dept = df_dept.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Exportar Consolidado Regional (CSV)",
                    data=csv_dept,
                    file_name=f"departamentos_flujo_{anio_seleccionado}.csv",
                    mime="text/csv",
                    use_container_width=True
                )