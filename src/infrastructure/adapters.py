from __future__ import annotations
import pyodbc
import logging
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class SqlServerAdapter:
    """Adaptador para conexiones a SQL Server con reintentos"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def execute_count_query(self, query: str) -> int:
        """
        Ejecuta una consulta de conteo y retorna el resultado
        
        Args:
            query: Consulta SQL que retorna un solo valor entero
            
        Returns:
            Número entero resultado de la consulta
            
        Raises:
            Exception: Si falla después de todos los reintentos
        """
        try:
            with pyodbc.connect(self.connection_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    if result:
                        return int(result[0])
                    return 0
        except Exception as e:
            logger.error(f"Error ejecutando consulta SQL: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            with pyodbc.connect(self.connection_string, timeout=5) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.warning(f"Fallo en test de conexión SQL: {str(e)}")
            return False
