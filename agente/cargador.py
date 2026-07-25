from pathlib import Path
import pandas as pd

CARPETA_DOCS = Path("documentos")


def cargar_dataframes() -> dict[str, pd.DataFrame]:
    """Carga los 4 CSVs y convierte columnas de fecha a datetime."""
    cosecha = pd.read_csv(CARPETA_DOCS / "cosecha_historica.csv", parse_dates=["fecha_siembra", "fecha_cosecha"])
    riego = pd.read_csv(CARPETA_DOCS / "riego_campos.csv", parse_dates=["fecha"])
    clima = pd.read_csv(CARPETA_DOCS / "clima_campos.csv", parse_dates=["fecha"])
    activos = pd.read_csv(CARPETA_DOCS / "campos_activos.csv", parse_dates=["fecha_siembra", "ultima_biometria"])

    return {
        "cosecha_historica": cosecha,
        "riego_campos": riego,
        "clima_campos": clima,
        "campos_activos": activos,
    }