# 🌾 Agente de Operaciones Agroindustriales — Challenge Alura Agente

Challenge final del programa **ONE AI FOR TECH** (Alura + Oracle Next
Education), track Tech Builder Latam. Un agente de inteligencia artificial
que responde preguntas en lenguaje natural sobre datos operativos de una
empresa agroindustrial de caña de azúcar, sin necesidad de abrir un solo
Excel o CSV manualmente.

**🔗 App en vivo:** [challenge-alura-agente-agro.streamlit.app](https://challenge-alura-agente-agro-jmkeqec7yvmxps8m48enuf.streamlit.app/)

---

## El problema que resuelve

En operaciones agroindustriales, los datos de cosecha, riego, clima y
seguimiento de campos suelen vivir repartidos en hojas de cálculo que solo
algunas personas saben interpretar. Responder algo tan simple como *"¿qué
campo rindió mejor esta campaña?"* implica abrir un Excel, filtrar,
ordenar y calcular a mano.

Este agente permite hacer esa misma pregunta en español natural y recibir
una respuesta calculada en segundos, directamente sobre los datos reales.

---

## Arquitectura

```
Usuario → Streamlit (chat) → Agente Pandas (LangChain) → Gemini (LLM)
                                     ↓
                        Ejecuta código Python real
                        sobre los DataFrames (pandas)
```

**Por qué un agente Pandas y no RAG tradicional:** un enfoque RAG (búsqueda
por similitud de texto) funciona bien para preguntas sobre documentos de
texto, pero falla en preguntas de agregación, ranking o comparación
("¿qué 5 campos tuvieron mejor rendimiento?") — recuperaría fragmentos
parecidos al azar, no el cálculo real sobre todos los datos. Por eso este
agente usa `create_pandas_dataframe_agent` de LangChain: el modelo escribe
y ejecuta código pandas real sobre los datos completos, así que las
respuestas están respaldadas por números exactos, no por texto recuperado.

**Alcance deliberadamente simple:** el agente responde cada pregunta usando
el dataset relevante, sin forzar cruces entre datasets salvo que la
pregunta lo requiera explícitamente (ver ejemplo 4 más abajo). Se priorizó
que cada respuesta sea confiable y verificable sobre un análisis multi-
dataset más ambicioso pero más frágil.

### Componentes

| Pieza | Herramienta | Rol |
|---|---|---|
| Datos | 4 CSVs sintéticos | Cosecha histórica, riego, clima, campos activos |
| Orquestación | LangChain (`langchain-experimental`) | Agente que decide qué código ejecutar |
| Ejecución | `PythonAstREPLTool` | Corre el código pandas generado |
| LLM | Gemini (`gemini-flash-lite-latest`) | Interpreta la pregunta y redacta la respuesta |
| Interfaz | Streamlit | Chat + KPIs + panel de razonamiento visible |
| Deploy | Streamlit Community Cloud | Hosting público gratuito |

---

## Los datos

Todos los datasets son **sintéticos**, generados con un script propio
(`generar_datos.py`, seed reproducible) — no son datos reales de ninguna
empresa. Están modelados sobre conocimiento real de operaciones
agroindustriales de caña de azúcar:

- **`cosecha_historica.csv`** — 40 campos cosechados en 2 campañas, con
  hectáreas, fechas, toneladas cosechadas y rendimiento de azúcar.
- **`riego_campos.csv`** — ~2,000 registros semanales de riego por campo.
- **`clima_campos.csv`** — ~1,200 registros climáticos por fundo.
- **`campos_activos.csv`** — 12 campos actualmente en curso, sin cosechar.

Las variables de riego y clima están correlacionadas intencionalmente con
el rendimiento (más riego + mejor cumplimiento + más lluvia → mejor
tn/ha), con ruido aleatorio para que no sea una relación perfecta ni obvia.

---

## Ejemplos de uso

**1. Ranking sobre cosecha histórica**

> **Pregunta:** ¿Qué 5 campos tuvieron mejor tn_por_ha en la campaña 2024-2025?

> **Respuesta:** Los 5 campos con mejor rendimiento fueron C-1030 (Santa
> Rosa, 90.90 tn/ha), C-1021 (Los Álamos, 84.62 tn/ha), C-1022 (San Ramón,
> 83.70 tn/ha), C-1028 (El Palmar, 81.37 tn/ha) y C-1023 (La Esperanza,
> 80.93 tn/ha).

**2. Consulta sobre riego**

> **Pregunta:** ¿Cuáles son los 5 registros con mayor volumen de riego?

> **Respuesta:** Los 5 registros de mayor volumen fueron liderados por el
> campo C-1012 (242.3 m³, riego por goteo), seguido de C-1023, C-1012
> nuevamente, y dos registros de C-1018 — todos con volúmenes entre 228 y
> 242 m³.

**3. Consulta sobre clima**

> **Pregunta:** ¿Qué fundo tuvo la mayor precipitación acumulada?

> **Respuesta:** El fundo Santa Rosa registró la mayor precipitación
> acumulada, con 1,423.1 mm.

**4. Análisis cruzado (el agente decide cruzar cuando la pregunta lo exige)**

> **Pregunta:** ¿Existe relación entre cumplimiento de riego y tn_por_ha?

> **Respuesta:** El agente cruzó `cosecha_historica` con `riego_campos`,
> calculó un coeficiente de correlación de 0.35 (positiva moderada) y un
> modelo lineal simple: por cada punto porcentual adicional de
> cumplimiento de riego, el rendimiento aumenta en promedio 0.18 tn/ha.

---

## Cómo ejecutarlo localmente

```bash
git clone https://github.com/JoshDevx/challenge-alura-agente-agro.git
cd challenge-alura-agente-agro

python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash
# o: .venv\Scripts\Activate.ps1    # PowerShell

pip install -r requirements.txt

cp .env.example .env               # agrega tu GEMINI_API_KEY / GOOGLE_API_KEY
streamlit run app.py
```

La API key de Gemini se obtiene gratis en
[aistudio.google.com/apikey](https://aistudio.google.com/apikey).

### Regenerar los datos (opcional)

```bash
python generar_datos.py
```

---

## Deploy

Desplegado en **Streamlit Community Cloud**, conectado directamente al
repositorio de GitHub — cada `git push` a `main` actualiza la app
automáticamente.

> El challenge sugiere OCI Compute como opción de deploy, pero deja
> explícitamente abierta la elección de herramienta. Se optó por Streamlit
> Community Cloud tras encontrar limitaciones puntuales de capacidad en
> las instancias Always Free de OCI (`VM.Standard.A1.Flex`) al momento de
> la entrega.

Las API keys se gestionan mediante **Secrets** de Streamlit Cloud (no se
suben `.env` reales al repositorio).

---

## Limitaciones conocidas

- **Ejecución de código por el LLM:** el agente usa
  `allow_dangerous_code=True`, necesario para que pueda ejecutar pandas
  real. Es una decisión razonable para esta demo (sin usuarios externos
  con entrada libre no controlada), pero **no debe usarse tal cual en un
  entorno con usuarios anónimos sin sandboxing adicional.**
- **Datos sintéticos:** los CSVs no representan una operación real; sirven
  para demostrar el patrón de solución, no como fuente de verdad
  agronómica.
- **Tier gratuito de Gemini:** sujeto a límites de solicitudes por minuto
  y por día; en uso intensivo puede requerir esperar entre consultas.

---

## Stack

Python · LangChain · `langchain-experimental` · Gemini API · Pandas ·
Streamlit · Streamlit Community Cloud