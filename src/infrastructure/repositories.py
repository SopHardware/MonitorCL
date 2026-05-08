from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..domain.entities import SyncSession, MetricSnapshot
from ..domain.repositories import ISyncSessionRepository, IMetricSnapshotRepository
from .database import SyncSessionORM, MetricSnapshotORM


class PostgresSessionRepository(ISyncSessionRepository):
    """Implementación de repositorio para sesiones usando PostgreSQL/SQLAlchemy"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save_session(self, session: SyncSession) -> SyncSession:
        """Guarda una sesión de sincronización"""
        try:
            # Verificar si la sesión ya existe
            existing = self.db_session.query(SyncSessionORM).filter(
                SyncSessionORM.id == str(session.id)
            ).first()
            
            if existing:
                # Actualizar existente
                existing.process_name = session.process_name
                existing.start_time = session.start_time
                existing.end_time = session.end_time
                existing.initial_count = session.initial_count
                existing.status = session.status.value
                existing.duration_seconds = session.duration_seconds
            else:
                # Crear nuevo
                orm_session = SyncSessionORM(
                    id=str(session.id),
                    process_name=session.process_name,
                    start_time=session.start_time,
                    end_time=session.end_time,
                    initial_count=session.initial_count,
                    status=session.status.value,
                    duration_seconds=session.duration_seconds
                )
                self.db_session.add(orm_session)
            
            self.db_session.commit()
            self.db_session.refresh(orm_session if not existing else existing)
            
            # Actualizar la entidad con el ID de la base de datos (si es necesario)
            return session
        except Exception as e:
            self.db_session.rollback()
            raise e

    def get_active_session(self, process_name: str) -> Optional[SyncSession]:
        """Obtiene la sesión activa para un proceso"""
        try:
            orm_session = self.db_session.query(SyncSessionORM).filter(
                and_(
                    SyncSessionORM.process_name == process_name,
                    SyncSessionORM.status == ProcessStatus.PENDING.value
                )
            ).first()
            
            if orm_session:
                return SyncSession(
                    id=UUID(orm_session.id),
                    process_name=orm_session.process_name,
                    start_time=orm_session.start_time,
                    end_time=orm_session.end_time,
                    initial_count=orm_session.initial_count,
                    status=ProcessStatus(orm_session.status),
                    duration_seconds=orm_session.duration_seconds
                )
            return None
        except Exception as e:
            raise e

    def get_recent_sessions(self, process_name: str, limit: int = 10) -> List[SyncSession]:
        """Obtiene las sesiones recientes de un proceso"""
        try:
            orm_sessions = self.db_session.query(SyncSessionORM).filter(
                SyncSessionORM.process_name == process_name
            ).order_by(
                SyncSessionORM.start_time.desc()
            ).limit(limit).all()
            
            return [
                SyncSession(
                    id=UUID(s.id),
                    process_name=s.process_name,
                    start_time=s.start_time,
                    end_time=s.end_time,
                    initial_count=s.initial_count,
                    status=ProcessStatus(s.status),
                    duration_seconds=s.duration_seconds
                )
                for s in orm_sessions
            ]
        except Exception as e:
            raise e


class PostgresSnapshotRepository(IMetricSnapshotRepository):
    """Implementación de repositorio para snapshots usando PostgreSQL/SQLAlchemy"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save_snapshot(self, snapshot: MetricSnapshot) -> MetricSnapshot:
        """Guarda un snapshot métrico"""
        try:
            orm_snapshot = MetricSnapshotORM(
                session_id=str(snapshot.session_id),
                captured_at=snapshot.captured_at,
                current_count=snapshot.current_count
            )
            self.db_session.add(orm_snapshot)
            self.db_session.commit()
            self.db_session.refresh(orm_snapshot)
            
            # Actualizar el ID generado por la base de datos
            snapshot.id = orm_snapshot.id
            return snapshot
        except Exception as e:
            self.db_session.rollback()
            raise e

    def get_snapshots_by_session(self, session_id: UUID) -> List[MetricSnapshot]:
        """Obtiene todos los snapshots de una sesión"""
        try:
            orm_snapshots = self.db_session.query(MetricSnapshotORM).filter(
                MetricSnapshotORM.session_id == str(session_id)
            ).order_by(
                MetricSnapshotORM.captured_at.asc()
            ).all()
            
            return [
                MetricSnapshot(
                    id=s.id,
                    session_id=UUID(s.session_id),
                    captured_at=s.captured_at,
                    current_count=s.current_count
                )
                for s in orm_snapshots
            ]
        except Exception as e:
            raise e
