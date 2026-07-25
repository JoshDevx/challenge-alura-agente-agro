import streamlit as st
from dotenv import load_dotenv
from agente.agente import crear_agente_pandas

load_dotenv()

st.set_page_config(page_title="Agente de Campos - Caña de Azúcar", page_icon="🌾")

st.title("🌾 Agente de Operaciones Agroindustriales")
st.caption(
    "Pregunta sobre cosecha histórica, riego, clima y campos activos, "
    "en lenguaje natural. El agente calcula sobre los datos reales, no adivina."
)


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

for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["texto"])

EJEMPLOS = [
    "¿Qué 5 campos tuvieron mejor tn_por_ha en la campaña 2024-2025?",
    "¿Existe relación entre cumplimiento de riego y tn_por_ha?",
    "¿Qué fundo tuvo más precipitación acumulada y cómo le fue en rendimiento?",
    "¿Cómo va el campo con más días transcurridos entre los campos activos?",
]

with st.sidebar:
    st.header("Ejemplos de preguntas")
    for ejemplo in EJEMPLOS:
        st.markdown(f"- {ejemplo}")
    if st.button("Limpiar conversación"):
        st.session_state.historial = []
        st.rerun()

pregunta = st.chat_input("Escribe tu pregunta sobre los campos...")

if pregunta:
    st.session_state.historial.append({"rol": "user", "texto": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Analizando los datos..."):
            try:
                resultado = agente.invoke({"input": pregunta})
                respuesta = resultado["output"]
            except Exception as error:
                respuesta = f"Ocurrió un error al procesar la consulta: {error}"
        st.markdown(respuesta)

    st.session_state.historial.append({"rol": "assistant", "texto": respuesta})