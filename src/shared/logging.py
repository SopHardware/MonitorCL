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
    log_error_file: str = "logs/errors.log",
    max_bytes: int = 10*1024*1024,  # 10 MB
    backup_count: int = 5
) -> None:
    """
    Configura el logging estructurado en formato JSON con rotación de archivos
    y archivo separado para errores.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta del archivo de log general
        log_error_file: Ruta del archivo de errores (solo ERROR y CRITICAL)
        max_bytes: Tamaño máximo antes de rotación
        backup_count: Número de archivos de backup a mantener
    """
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar formato JSON
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)
            log_record['timestamp'] = record.created
            log_record['level'] = record.levelname
            log_record['logger'] = record.name
    
    json_formatter = CustomJsonFormatter(
        fmt='%(timestamp)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d',
    )
    
    # Handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(json_formatter)
    
    # Handler específico para errores (archivo separado)
    class ErrorFilter(logging.Filter):
        def filter(self, record):
            return record.levelno >= logging.ERROR
    
    error_handler = logging.handlers.RotatingFileHandler(
        log_error_file,
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3
    )
    error_handler.setFormatter(json_formatter)
    error_handler.addFilter(ErrorFilter())
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    
    # Configurar logger raíz
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=[file_handler, error_handler, console_handler]
    )
    
    # Reducir ruido de librerías externas
    logging.getLogger("pyodbc").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logging.info("Logging configurado exitosamente")
