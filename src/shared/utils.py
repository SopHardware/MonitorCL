from __future__ import annotations
import re
from datetime import datetime, time
from typing import Optional
import pyodbc


def is_within_time_window(
    current_time: datetime,
    start_time: str,
    end_time: str
) -> bool:
    """
    Verifica si una hora está dentro de una ventana de tiempo
    
    Args:
        current_time: Hora actual a verificar
        start_time: Hora de inicio en formato HH:MM
        end_time: Hora de fin en formato HH:MM
        
    Returns:
        True si está dentro de la ventana, False en caso contrario
    """
    try:
        start = time.fromisoformat(start_time)
        end = time.fromisoformat(end_time)
        current = current_time.time()
        
        if start <= end:
            # Ventana normal (no cruza medianoche)
            return start <= current <= end
        else:
            # Ventana que cruza medianoche (ej: 22:00 a 06:00)
            return start <= current or current <= end
    except ValueError as e:
        raise ValueError(f"Formato de hora inválido: {e}")


def get_mssql_connection_string(
    host: str,
    user: str,
    password: str,
    database: str = "master",
    port: int = 1433,
    timeout: int = 30,
    driver: str = None
) -> str:
    """
    Construye una cadena de conexión para SQL Server usando pyodbc
    
    Args:
        host: Hostname o IP del servidor SQL
        user: Usuario para autenticación
        password: Contraseña para autenticación
        database: Base de datos a conectar (default: master)
        port: Puerto SQL Server (default: 1433)
        timeout: Timeout de conexión en segundos (default: 30)
        driver: Driver específico (auto-detecta para SQL 2000)
        
    Returns:
        Cadena de conexión para pyodbc
    """
    # Auto-detectar driver para SQL 2000 (CL)
    if driver is None:
        if host == "192.168.20.19":
            driver = "{SQL Server}"
        else:
            driver = "{ODBC Driver 17 for SQL Server}"
    
    conn_params = [
        f"DRIVER={driver};",
        f"SERVER={host},{port};",
        f"DATABASE={database};",
        f"UID={user};",
        f"PWD={password};",
    ]
    
    # Solo agregar opciones de SSL para drivers modernos (no SQL 2000)
    if driver != "{SQL Server}":
        conn_params.append(f"Timeout={timeout};")
        conn_params.append(f"Encrypt=yes;")
        conn_params.append(f"TrustServerCertificate=yes;")
    
    conn_params.append(f"Connection Timeout={timeout};")
    
    return "".join(conn_params)


def safe_int(value: Any, default: int = 0) -> int:
    """
    Convierte un valor a entero de forma segura
    
    Args:
        value: Valor a convertir
        default: Valor por defecto si la conversión falla
        
    Returns:
        Valor entero o el valor por defecto
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def truncate_string(text: str, max_length: int = 100) -> str:
    """
    Trunca una cadena a una longitud máxima
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima permitida
        
    Returns:
        Texto truncado con "..." si excede la longitud máxima
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def generate_correlation_id() -> str:
    """
    Genera un ID de correlación único para tracking
    
    Returns:
        UUID v4 como string
    """
    import uuid
    return str(uuid.uuid4())
