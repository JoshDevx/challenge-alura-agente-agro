from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from agente.cargador import cargar_dataframes

DESCRIPCION_DATASETS = """
Tienes acceso a 4 DataFrames de operaciones agroindustriales de caña de azúcar:

1. cosecha_historica: un registro por campo ya cosechado (campana, fundo, variedad,
   hectareas, fecha_siembra, fecha_cosecha, tn_cosechadas, tn_por_ha, rendimiento_azucar_pct).
2. riego_campos: registros semanales de riego por campo (codigo_campo, fecha,
   tipo_riego, volumen_m3, horas_riego, cumplimiento_pct).
3. clima_campos: registros climáticos cada 3 días POR FUNDO, no por campo
   (fundo, fecha, temp_max, temp_min, precipitacion_mm, humedad_pct, radiacion_mj_m2).
4. campos_activos: campos que aún no se cosechan (codigo_campo, fundo, variedad,
   hectareas, dias_transcurridos, estado, ultima_biometria,
   volumen_riego_acumulado_m3, cumplimiento_riego_pct).

Reglas al responder:
- Para relacionar riego/cosecha con clima, une por 'fundo' (el clima no tiene codigo_campo).
- Si la pregunta pide una proyección o estimación sobre un campo activo, acláralo
  explícitamente como una ESTIMACIÓN basada en el histórico, nunca como un hecho.
- Siempre que sea posible, respalda la respuesta con el número exacto calculado,
  no una impresión general.
- Responde en español, con el vocabulario del sector (fundo, campana, tn/ha).
"""


def crear_agente_pandas():
    dataframes = cargar_dataframes()
    lista_df = list(dataframes.values())
    nombres = list(dataframes.keys())

    modelo = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

    agente = create_pandas_dataframe_agent(
        modelo,
        lista_df,
        verbose=True,
        agent_type="tool-calling",
        prefix=DESCRIPCION_DATASETS + "\nLos DataFrames se llaman: " + ", ".join(
            f"df{i+1}={nombre}" for i, nombre in enumerate(nombres)
        ),
        allow_dangerous_code=True,  # el agente ejecuta código Python real, ver nota de seguridad abajo
        number_of_head_rows=5,
    )
    return agente