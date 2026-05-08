from __future__ import annotations
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from enum import Enum as PyEnum
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class ProcessStatusORM(PyEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SyncSessionORM(Base):
    __tablename__ = "sync_sessions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    process_name = Column(String(100), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    initial_count = Column(Integer, nullable=False, default=0)
    status = Column(Enum(ProcessStatusORM), nullable=False, default=ProcessStatusORM.PENDING)
    duration_seconds = Column(Integer, nullable=True)


class MetricSnapshotORM(Base):
    __tablename__ = "sync_snapshots"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    session_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    captured_at = Column(DateTime, nullable=False)
    current_count = Column(Integer, nullable=False, default=0)


def get_database_url() -> str:
    """Construye la URL de conexión a PostgreSQL desde variables de entorno"""
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "db_metrics")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def get_engine():
    """Crea y retorna el motor de SQLAlchemy"""
    database_url = get_database_url()
    return create_engine(database_url, echo=False)


def get_session_local():
    """Crea y retorna una fábrica de sesiones"""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Crea todas las tablas definidas en los modelos"""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
