import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from agente.agente import crear_agente_pandas

load_dotenv()

# Compatibilidad: Streamlit Cloud usa st.secrets, local usa .env
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title="Agente de Campos - Caña de Azúcar", page_icon="🌾", layout="centered")

st.title("🌾 Agente de Operaciones Agroindustriales")
st.caption(
    "Pregunta sobre cosecha histórica, riego, clima y campos activos, "
    "en lenguaje natural. El agente calcula sobre los datos reales, no adivina."
)

# ---------------------------------------------------------------------------
# KPIs rápidos (no usan el agente, solo lectura directa para que carguen al instante)
# ---------------------------------------------------------------------------
try:
    _df_cosecha_kpi = pd.read_csv("documentos/cosecha_historica.csv")
    _df_activos_kpi = pd.read_csv("documentos/campos_activos.csv")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Campos históricos", len(_df_cosecha_kpi))
    col2.metric("Rendimiento promedio", f"{_df_cosecha_kpi['tn_por_ha'].mean():.1f} tn/ha")
    col3.metric("Fundos", _df_cosecha_kpi["fundo"].nunique())
    col4.metric("Campos activos", len(_df_activos_kpi))
except FileNotFoundError:
    st.warning("No se encontraron los CSVs en 'documentos/' para mostrar los KPIs.")

st.divider()


@st.cache_resource(show_spinner="Cargando datos y preparando el agente...")
def cargar_agente():
    return crear_agente_pandas()


try:
    agente = cargar_agente()
except Exception as error:
    st.error(f"No se pudo iniciar el agente: {error}")
    st.stop()

if "historial" not in st.session_state:
    st.session_state.historial = []

if "pregunta_pendiente" not in st.session_state:
    st.session_state.pregunta_pendiente = None

EJEMPLOS = [
    "¿Qué 5 campos tuvieron mejor tn_por_ha en la campaña 2024-2025?",
    "¿Cuáles son los 5 registros con mayor volumen de riego?",
    "¿Qué fundo tuvo la mayor precipitación acumulada?",
    "¿Cómo va el campo con más días transcurridos entre los activos?",
]

with st.sidebar:
    st.header("🌱 Sobre el agente")
    st.markdown(
        "Responde preguntas sobre documentación operativa de caña de azúcar: "
        "cosecha histórica, riego, clima y campos actualmente en curso. "
        "Los datos son sintéticos, generados con seed reproducible."
    )
    st.divider()
    st.subheader("Prueba con:")
    for i, ejemplo in enumerate(EJEMPLOS):
        if st.button(ejemplo, key=f"ejemplo_{i}", use_container_width=True):
            st.session_state.pregunta_pendiente = ejemplo

    st.divider()
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.historial = []
        st.rerun()

# ---------------------------------------------------------------------------
# Historial de chat
# ---------------------------------------------------------------------------
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

# ---------------------------------------------------------------------------
# Entrada: por chat o por botón de ejemplo
# ---------------------------------------------------------------------------
pregunta_escrita = st.chat_input("Escribe tu pregunta sobre los campos...")
pregunta = pregunta_escrita or st.session_state.pregunta_pendiente
st.session_state.pregunta_pendiente = None

if pregunta:
    st.session_state.historial.append({"rol": "user", "texto": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        contenedor_pensamiento = st.container()
        callback = StreamlitCallbackHandler(
            contenedor_pensamiento,
            expand_new_thoughts=False,
            collapse_completed_thoughts=True,
        )
        try:
            resultado = agente.invoke({"input": pregunta}, config={"callbacks": [callback]})
            respuesta = resultado["output"]
        except Exception as error:
            respuesta = f"Ocurrió un error al procesar la consulta: {error}"
        st.markdown(respuesta)

    st.session_state.historial.append({"rol": "assistant", "texto": respuesta})
