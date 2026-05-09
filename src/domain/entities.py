from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional


class ProcessStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class SyncSession:
    """Entidad que representa una sesión de sincronización"""
    process_name: str
    start_time: datetime
    id: UUID = field(default_factory=uuid4)
    end_time: Optional[datetime] = None
    initial_count: int = 0
    status: ProcessStatus = ProcessStatus.PENDING
    duration_seconds: Optional[int] = None

    def close_session(self, end_time: datetime) -> None:
        """Cierra la sesión y calcula la duración"""
        self.end_time = end_time
        self.status = ProcessStatus.COMPLETED
        if self.start_time and self.end_time:
            self.duration_seconds = int((self.end_time - self.start_time).total_seconds())

    def is_active(self) -> bool:
        """Verifica si la sesión está activa"""
        return self.status == ProcessStatus.PENDING


@dataclass
class MetricSnapshot:
    """Entidad que representa una captura métrica en un punto en tiempo"""
    session_id: UUID
    captured_at: datetime
    current_count: int
    id: int = field(default_factory=lambda: 0)  # Se asignará en BD

    def format_duration(self, start_time: datetime) -> str:
        """Formatea la duración desde inicio de sesión"""
        if not start_time:
            return "-"
        elapsed = int((self.captured_at - start_time).total_seconds())
        return format_duration(elapsed)


@dataclass
class ProcessMetrics:
    """Métricas en memoria para un proceso"""
    process_key: str
    session: Optional[SyncSession] = None
    snapshots: list = field(default_factory=list)
    error_count: int = 0
    last_error: str = ""
    
    def add_snapshot(self, count: int) -> None:
        """Agrega un snapshot"""
        snapshot = MetricSnapshot(
            session_id=self.session.id if self.session else uuid4(),
            captured_at=datetime.now(),
            current_count=count
        )
        self.snapshots.append(snapshot)
    
    def start_session(self, count: int) -> None:
        """Inicia una nueva sesión"""
        self.session = SyncSession(
            process_name=self.process_key,
            start_time=datetime.now(),
            initial_count=count
        )
        self.snapshots.clear()
        self.error_count = 0
    
    def close_session(self) -> Optional[SyncSession]:
        """Cierra la sesión actual"""
        if self.session and self.session.is_active():
            self.session.close_session(datetime.now())
            result = self.session
            self.session = None
            return result
        return None
    
    def get_duration(self) -> str:
        """Obtiene duración formateada"""
        if not self.session or not self.session.start_time:
            return "-"
        elapsed = int((datetime.now() - self.session.start_time).total_seconds())
        return format_duration(elapsed)
    
    def reset_errors(self) -> None:
        """Resetea contador de errores"""
        self.error_count = 0
        self.last_error = ""
    
    def increment_error(self, error: str) -> None:
        """Incrementa contador de errores"""
        self.error_count += 1
        self.last_error = error
    
    def has_critical_failure(self) -> bool:
        """Verifica si hay fallo crítico (3+ errores)"""
        return self.error_count >= 3


def format_duration(seconds: int) -> str:
    """Formatea segundos a HH:MM:SS"""
    if seconds < 0:
        return "00:00:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
