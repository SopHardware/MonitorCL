from __future__ import annotations
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings"""
    
    # Información de la aplicación
    APP_NAME: str = Field(default="SyncSentinel", env="APP_NAME")
    APP_ENV: str = Field(default="development", env="APP_ENV")
    
    # Configuración de horarios (formato HH:MM)
    MONITOR_START_TIME: str = Field(default="18:30", env="MONITOR_START_TIME")  # 6:30 PM
    MONITOR_END_TIME: str = Field(default="06:00", env="MONITOR_END_TIME")  # 6:00 AM
    CHECK_INTERVAL_SECONDS: int = Field(default=600, env="CHECK_INTERVAL_SECONDS")  # 10 minutos
    
    # Credenciales SQL Server (usando autenticación SQL)
    MSSQL_USER: str = Field(..., env="MSSQL_USER")
    MSSQL_PASS: str = Field(..., env="MSSQL_PASS")
    
    # Hosts de los nodos SQL Server
    HOST_GAINS: str = Field(..., env="HOST_GAINS")
    HOST_REPLICA: str = Field(..., env="HOST_REPLICA")
    HOST_EPICOR: str = Field(..., env="HOST_EPICOR")
    HOST_CL: str = Field(..., env="HOST_CL")
    
    # Bases de datos de los nodos SQL Server
    MSSQL_DB_GAINS: str = Field(default="master", env="MSSQL_DB_GAINS")
    MSSQL_DB_REPLICA: str = Field(default="master", env="MSSQL_DB_REPLICA")
    MSSQL_DB_EPICOR: str = Field(default="master", env="MSSQL_DB_EPICOR")
    MSSQL_DB_CL: str = Field(default="master", env="MSSQL_DB_CL")
    
    # Configuración PostgreSQL
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: str = Field(default="5432", env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="db_metrics", env="POSTGRES_DB")
    
    # Notificaciones
    SLACK_WEBHOOK_URL: str = Field(..., env="SLACK_WEBHOOK_URL")
    
    # Configuración de fechas para queries
    START_DATE_DAYS_BACK: int = Field(default=30, env="START_DATE_DAYS_BACK")
    
    @field_validator('MONITOR_START_TIME', 'MONITOR_END_TIME')
    def validate_time_format(cls, v):
        """Valida que el tiempo esté en formato HH:MM"""
        try:
            parts = v.split(':')
            if len(parts) != 2:
                raise ValueError('Formato debe ser HH:MM')
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError('Hora fuera de rango')
            return v
        except ValueError as e:
            raise ValueError(f'Formato de tiempo inválido "{v}": {e}')
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()
