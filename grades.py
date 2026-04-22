import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard Prof. Santiago Lomelí García", layout="wide", initial_sidebar_state="expanded")

# --- PALETA DE COLORES RETROFUTURISTA ---
PALETA = {
    'fondo': '#0a0d0a',        # Negro verdoso profundo
    'neon_naranja': '#ff9100', # Ámbar brillante
    'neon_verde': '#39ff14',   # Verde radioactivo
    'neon_esmeralda': '#008f11', # Verde terminal antigua
    'reprobado_bg': '#2a0000',
    'reprobado_text': '#ff4444'
}

# Estilo CSS Cyberpunk
st.markdown(f"""
    <style>
    .main {{ background-color: {PALETA['fondo']}; }}
    .stMetric {{ 
        background-color: #0f1a0f; 
        border: 1px solid {PALETA['neon_verde']}; 
        border-radius: 10px; 
        padding: 10px; 
    }}
    div[data-testid="stMetricValue"] {{ color: {PALETA['neon_naranja']}; }}
    div[data-testid="stExpander"] {{ background-color: #0f1a0f; border: 1px solid {PALETA['neon_naranja']}; }}
    h1, h2, h3, p, span, label {{ color: #e0e0e0 !important; }}
    div[data-testid="stNotification"] {{ background-color: #1a1a1a; border-radius: 10px; }}
    /* Estilo para el uploader */
    .stFileUploader {{ border: 1px dashed {PALETA['neon_verde']}; padding: 10px; border-radius: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGAR DATOS ---
@st.cache_data
def process_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        columns_map = {
            df.columns[0]: 'Nombre',
            df.columns[2]: 'Parcial_1',
            df.columns[3]: 'Parcial_2',
            df.columns[-1]: 'Calificacion_Actual'
        }
        df = df.rename(columns=columns_map)
        df = df[df['Nombre'] != 'Points Possible'].copy()
        
        cols = ['Parcial_1', 'Parcial_2', 'Calificacion_Actual']
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df.dropna(subset=['Calificacion_Actual']), cols
    except Exception as e:
        st.error(f"SYSTEM ERROR: FALLO EN PROCESAMIENTO: {e}")
        return pd.DataFrame(), []

# --- 3. FUNCIONES DE APOYO ---
def obtener_color_nota(nota):
    if nota >= 80: return PALETA['neon_verde']
    elif 60 <= nota < 80: return PALETA['neon_naranja']
    else: return PALETA['reprobado_text']

def resaltar_reprobados(val):
    if val < 60:
        return f'background-color: {PALETA["reprobado_bg"]}; color: {PALETA["reprobado_text"]}; font-weight: bold; border: 1px solid {PALETA["reprobado_text"]}'
    return f'color: {PALETA["neon_verde"]}'

# --- 4. SIDEBAR MENU & FILE UPLOADER ---
with st.sidebar:
    st.markdown(f"### ⚡ ACCESO A DATOS")
    archivo_cargado = st.file_uploader("Cargar archivo CSV", type=["csv"])
    
    st.markdown("---")
    
    selected = option_menu(
        menu_title="DASHBOARD",
        options=["Inicio", "Dashboard Alumno", "Estadísticas Grupal", "Configuración"],
        icons=["house", "person-badge", "graph-up-arrow", "gear"],
        menu_icon="terminal", 
        default_index=0,
        styles={
            "container": {"background-color": "#0a110a"},
            "icon": {"color": PALETA['neon_naranja'], "font-size": "20px"}, 
            "nav-link": {"color": "white", "text-align": "left"},
            "nav-link-selected": {"background-color": PALETA['neon_esmeralda']},
        }
    )

    df = pd.DataFrame()
    cols_eval = []

    if archivo_cargado is not None:
        df, cols_eval = process_data(archivo_cargado)
        st.markdown("---")
        alumno_sel = st.selectbox("🎯 Target Alumno:", sorted(df['Nombre'].unique()))
    else:
        st.info("Esperando carga de base de datos...")

# --- 5. LÓGICA DE NAVEGACIÓN ---

if archivo_cargado is None:
    st.title("📟 DASHBOARD 2026_01")
    st.warning("POR FAVOR, CARGUE EL ARCHIVO 'DE2026.csv' o 'EA2026.csv' DESDE EL PANEL LATERAL PARA INICIAR EL ESCANEO.")
    st.image("https://img.freepik.com/free-photo/circuit-board-close-up-with-different-components_23-2149174327.jpg")
elif df.empty:
    st.error("CORE ERROR: DATASTREAM OFFLINE - El archivo no tiene el formato esperado.")

elif selected == "Inicio":
    st.title("Dashboard de Evaluación Académica - Prof. Santiago Lomelí García")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("UNIDADES DETECTADAS", len(df))
    c2.metric("PROMEDIO CORE", f"{round(df['Calificacion_Actual'].mean(), 1)}")
    c3.metric("VIABILIDAD GRUPAL", f"{round((df['Calificacion_Actual'] >= 60).sum() / len(df) * 100)}%")

    st.markdown("---")
    st.subheader(f"Base de Datos Maestra ({len(df)} registros)")
    
    df_styled = df.style.applymap(resaltar_reprobados, subset=['Calificacion_Actual'])
    st.dataframe(df_styled, use_container_width=True, height=800)

elif selected == "Dashboard Alumno":
    st.header(f"📌 Perfil Seleccionado: {alumno_sel}")
    datos_alumno = df[df['Nombre'] == alumno_sel].iloc[0]
    
    nota_actual = datos_alumno['Calificacion_Actual']
    
    if nota_actual < 60:
        st.warning(f"⚠️ **ALERTA CRÍTICA:** Nivel de integridad inferior al umbral ({nota_actual}). Se ha detectado una probabilidad de fallo inminente. Requiere intervención.")
    elif nota_actual < 70:
        st.info(f"ℹ️ **AVISO DE SISTEMA:** Rendimiento en zona de transición ({nota_actual}).")
    else:
        st.success(f"✅ **SISTEMA ESTABLE:** Viabilidad operativa confirmada.")

    c1, c2, c3 = st.columns(3)
    for i, col in enumerate(cols_eval):
        val = datos_alumno[col]
        avg = df[col].mean()
        [c1, c2, c3][i].metric(col, val, f"{round(val - avg, 1)} vs Grupo")

    st.markdown("---")
    st.subheader("Visualización de Rendimiento")
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=cols_eval, y=[datos_alumno[c] for c in cols_eval], 
        name='Individual', marker_color=PALETA['neon_naranja'],
        marker_line=dict(color=PALETA['neon_verde'], width=2)
    ))
    fig_bar.add_trace(go.Bar(
        x=cols_eval, y=[df[c].mean() for c in cols_eval], 
        name='Global Average', marker_color='rgba(57, 255, 20, 0.1)',
        marker_line=dict(color=PALETA['neon_esmeralda'], width=1)
    ))
    
    fig_bar.update_layout(
        barmode='group', template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color=PALETA['neon_verde']
    )
    st.plotly_chart(fig_bar, use_container_width=True)

elif selected == "Estadísticas Grupal":
    st.header("Análisis de posicionamiento individual")
    st.write(f"Ubicación de: **{alumno_sel}**")
    datos_alumno = df[df['Nombre'] == alumno_sel].iloc[0]

    for col in cols_eval:
        nota_alumno = datos_alumno[col]
        color_ind = obtener_color_nota(nota_alumno)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.07, row_heights=[0.3, 0.7])

        fig.add_trace(go.Box(
            x=df[col], name="Distribución",
            jitter=0.5, pointpos=-1.8, boxpoints='all',
            marker=dict(color=PALETA['neon_verde'], size=3),
            line_color=PALETA['neon_naranja'], fillcolor='#0f1a0f',
            orientation='h'
        ), row=1, col=1)

        fig.add_trace(go.Histogram(
            x=df[col], name="Frecuencia", nbinsx=15,
            marker=dict(color=PALETA['neon_esmeralda'], line=dict(color=PALETA['neon_verde'], width=1)),
            opacity=0.6
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=[nota_alumno], y=["Distribución"], mode='markers',
            marker=dict(color='white', size=15, symbol='star',
                        line=dict(width=3, color=PALETA['neon_naranja'])),
            name="TARGET"
        ), row=1, col=1)

        fig.add_vline(x=nota_alumno, line_dash="dash", line_color=PALETA['neon_naranja'], line_width=4, row=2, col=1)

        fig.update_layout(
            template="plotly_dark", paper_bgcolor=PALETA['fondo'], plot_bgcolor='#0a110a',
            font_color=PALETA['neon_naranja'], height=500, showlegend=False
        )
        fig.update_yaxes(showticklabels=False, row=1, col=1)
        st.plotly_chart(fig, use_container_width=True)

elif selected == "Configuración":
    st.header("⚙️ Core Settings")
    if st.button("🔄 REBOOT SYSTEM (Clear Cache)"):
        st.cache_data.clear()
        st.success("Sincronización completa. Reiniciando flujos de datos...")
        st.rerun()