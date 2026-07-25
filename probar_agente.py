# probar_agente.py
from dotenv import load_dotenv
load_dotenv()

from agente.agente import crear_agente_pandas

agente = crear_agente_pandas()
resultado = agente.invoke({"input": "¿Qué fundo tuvo la mayor precipitación acumulada en clima_campos?"})
print(resultado["output"])