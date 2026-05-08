from __future__ import annotations
from typing import Any, Dict, Optional


class SyncSentinelException(Exception):
    """Excepción base para todas las excepciones del sistema SyncSentinel"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a un diccionario para logging o serialization"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class DatabaseConnectionError(SyncSentinelException):
    """Error al conectar con cualquier base de datos"""
    pass


class QueryExecutionError(SyncSentinelException):
    """Error al ejecutar una consulta SQL"""
    pass


class SlackNotificationError(SyncSentinelException):
    """Error al enviar notificaciones a Slack"""
    pass


class ConfigurationError(SyncSentinelException):
    """Error en la configuración de la aplicación"""
    pass


class ProcessMonitoringError(SyncSentinelException):
    """Error durante el monitoreo de un proceso"""
    pass
