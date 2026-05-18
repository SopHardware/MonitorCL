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
<<<<<<< HEAD
    backup_count: int = 5,
    app_env: str = "development"
=======
    backup_count: int = 5
>>>>>>> origin/main
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
<<<<<<< HEAD
        app_env: Entorno de la aplicación (Dev/Development habilita logs en archivo)
    """
    write_to_file = app_env.lower() in ["dev", "development"]
    
    # Crear directorio de logs si no existe y está habilitado
    if write_to_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
=======
    """
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
>>>>>>> origin/main
    
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
    
<<<<<<< HEAD
    handlers = []
    
    # Handler para consola (siempre activo)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    handlers.append(console_handler)
    
    # Handlers para archivo (solo en Dev/Development)
    if write_to_file:
        # Handler para archivo con rotación
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(json_formatter)
        handlers.append(file_handler)
        
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
        handlers.append(error_handler)
=======
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
>>>>>>> origin/main
    
    # Configurar logger raíz
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
<<<<<<< HEAD
        handlers=handlers
=======
        handlers=[file_handler, error_handler, console_handler]
>>>>>>> origin/main
    )
    
    # Reducir ruido de librerías externas
    logging.getLogger("pyodbc").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
<<<<<<< HEAD
    if write_to_file:
        logging.info("Logging configurado exitosamente (archivo + consola)")
    else:
        logging.info("Logging configurado exitosamente (solo consola)")
=======
    logging.info("Logging configurado exitosamente")
>>>>>>> origin/main
