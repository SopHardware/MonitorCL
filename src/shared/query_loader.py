from __future__ import annotations
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

QUERIES_DIR = Path(__file__).parent.parent.parent / "queries"


def load_query(filename: str) -> str:
    """
    Carga un query desde un archivo .sql y reemplaza placeholders dinámicos.
    
    Args:
        filename: Nombre del archivo SQL (ej: 'gains_aprobaciones.sql')
        
    Returns:
        El contenido del query con placeholders reemplazados
    """
    query_path = QUERIES_DIR / filename
    
    if not query_path.exists():
        logger.error(f"Query file not found: {query_path}")
        raise FileNotFoundError(f"Query file not found: {filename}")
    
    with open(query_path, "r", encoding="utf-8") as f:
        query = f.read()
    
    return query


def get_start_date(days_back: int) -> str:
    """
    Calcula la fecha de inicio para los queries.
    
    Args:
        days_back: Número de días hacia atrás
        
    Returns:
        Fecha en formato YYYY-MM-DD
    """
    start_date = datetime.now() - timedelta(days=days_back)
    return start_date.strftime("%Y-%m-%d")


def process_query(query: str, start_date_days_back: int = 30) -> str:
    """
    Procesa un query reemplazando placeholders dinámicos.
    
    Args:
        query: Query con placeholders
        start_date_days_back: Días hacia atrás para calcular @START_DATE@
        
    Returns:
        Query procesado lista para ejecutar
    """
    start_date = get_start_date(start_date_days_back)
    processed = query.replace("@START_DATE@", start_date)
    
    return processed


def load_query_file(filename: str, start_date_days_back: int = 30) -> str:
    """
    Carga y procesa un query desde archivo.
    
    Args:
        filename: Nombre del archivo SQL
        start_date_days_back: Días hacia atrás para calcular fecha
        
    Returns:
        Query procesada lista para ejecutar
    """
    query = load_query(filename)
    return process_query(query, start_date_days_back)


QUERY_FILES: Dict[str, str] = {
    "GAINS_3.66": "gains_aprobaciones.sql",
    "REPLICA_3.83": "replica_aprobaciones.sql",
    "MATERIAL_CL_REPLICA": "cl_material.sql",
    "EPICOR_3.72": "epicor_reprocesamiento.sql",
    "EMBARQUES_CL_REPLICA": "cl_embarques.sql",
    "REPLICA_EPICOR": "replica_epicor.sql",
    "REPLICA_CL": "replica_cl.sql",
    "EPICOR_SHIP": "epicor_ship.sql",
}


def get_process_query(process_key: str, start_date_days_back: int = 30) -> str:
    """
    Obtiene el query para un proceso específico.
    
    Args:
        process_key: Clave del proceso (ej: 'GAINS_3.66')
        start_date_days_back: Días hacia atrás para fecha
        
    Returns:
        Query procesada lista para ejecutar
    """
    if process_key not in QUERY_FILES:
        raise ValueError(f"Unknown process key: {process_key}")
    
    filename = QUERY_FILES[process_key]
    return load_query_file(filename, start_date_days_back)


def get_all_query_files() -> Dict[str, str]:
    """
    Retorna el mapeo de procesos a archivos SQL.
    
    Returns:
        Dictionary con process_key -> filename
    """
    return QUERY_FILES.copy()