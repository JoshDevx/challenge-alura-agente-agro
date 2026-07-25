# probar_agente.py
from dotenv import load_dotenv
load_dotenv()

from agente.agente import crear_agente_pandas

agente = crear_agente_pandas()
resultado = agente.invoke({"input": "¿Qué 5 campos tuvieron mejor tn_por_ha en la campaña 2024-2025?"})
print(resultado["output"])