from __future__ import annotations
import json
import logging
import logging.handlers
import os
import sys
from typing import Any, Dict
from pythonjsonlogger import jsonlogger

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/syncsentinel.log",
    max_bytes: int = 10*1024*1024,  # 10 MB
    backup_count: int = 5
) -> None:
    """
    Configura el logging estructurado en formato JSON con rotación de archivos
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta del archivo de log
        max_bytes: Tamaño máximo antes de rotación
        backup_count: Número de archivos de backup a mantener
    """
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar formato JSON
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d',
        rename_fields={"levelname": "level", "asctime": "timestamp"}
    )
    
    # Handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(json_formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    
    # Configurar logger raíz
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=[file_handler, console_handler]
    )
    
    # Reducir ruido de librerías externas
    logging.getLogger("pyodbc").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logging.info("Logging configurado exitosamente")
