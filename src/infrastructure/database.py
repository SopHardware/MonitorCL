from __future__ import annotations
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger, event, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.pool import QueuePool
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class SyncSessionORM(Base):
    __tablename__ = "sync_sessions"
    __table_args__ = {
        'schema': 'CL',
        'sqlite_autoincrement': False,
    }

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    process_name = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    initial_count = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default='PENDING')
    duration_seconds = Column(Integer, nullable=True)


class MetricSnapshotORM(Base):
    __tablename__ = "sync_snapshots"
    __table_args__ = {
        'schema': 'CL',
        'sqlite_autoincrement': False,
    }

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(PG_UUID(as_uuid=True), nullable=False)
    captured_at = Column(DateTime, nullable=False)
    current_count = Column(Integer, nullable=False, default=0)


def get_database_url() -> str:
    """Construye la URL de conexión a PostgreSQL desde variables de entorno"""
    user = os.getenv("POSTGRES_USER", "user_monitores_app")
    password = os.getenv("POSTGRES_PASSWORD", "")
    host = os.getenv("POSTGRES_HOST", "10.40.3.170")
    port = os.getenv("POSTGRES_PORT", "5433")
    database = os.getenv("POSTGRES_DB", "Monitores")
    
    # URL encode password para caracteres especiales (@, #, etc.)
    password_encoded = quote_plus(password)
    
    return f"postgresql://{user}:{password_encoded}@{host}:{port}/{database}"


def get_engine():
    """Crea y retorna el motor de SQLAlchemy"""
    database_url = get_database_url()
    schema = os.getenv("POSTGRES_SCHEMA", "CL")
    
    engine = create_engine(
        database_url,
        echo=False,
        poolclass=QueuePool,
        pool_pre_ping=True
    )
    
    # Settear schema en cada conexión
    @event.listens_for(engine, "connect")
    def set_search_path(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute(f'SET search_path TO {schema}')
        cursor.execute("COMMIT")
        cursor.close()
    
    return engine


def get_session_local():
    """Crea y retorna una fábrica de sesiones"""
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Crea todas las tablas definidas en los modelos"""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
