from __future__ import annotations
from typing import List, Optional
from uuid import UUID
import psycopg2
import os
from dotenv import load_dotenv
from ..domain.entities import SyncSession, MetricSnapshot, ProcessStatus

load_dotenv()


class PostgresSessionRepository:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or cls._connection.closed:
            pwd = os.getenv("POSTGRES_PASSWORD", "") or ""
            cls._connection = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "10.40.3.170"),
                port=os.getenv("POSTGRES_PORT", "5433"),
                database=os.getenv("POSTGRES_DB", "Monitores"),
                user=os.getenv("POSTGRES_USER", "user_monitores_app"),
                password=pwd)
            cls._connection.autocommit = True
        return cls._connection

    def save_session(self, session: SyncSession) -> SyncSession:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM "CL".sync_sessions WHERE id = %s', [str(session.id)])
        exists = cursor.fetchone()
        if exists:
            cursor.execute('UPDATE "CL".sync_sessions SET process_name = %s, start_time = %s, end_time = %s, initial_count = %s, status = %s, duration_seconds = %s WHERE id = %s',
                [session.process_name, session.start_time, session.end_time, session.initial_count, session.status.value, session.duration_seconds, str(session.id)])
        else:
            cursor.execute('INSERT INTO "CL".sync_sessions (id, process_name, start_time, end_time, initial_count, status, duration_seconds) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                [str(session.id), session.process_name, session.start_time, session.end_time, session.initial_count, session.status.value, session.duration_seconds])
        cursor.close()
        return session

    def get_active_session(self, process_name: str) -> Optional[SyncSession]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, process_name, start_time, end_time, initial_count, status, duration_seconds FROM "CL".sync_sessions WHERE process_name = %s AND status = %s ORDER BY start_time DESC LIMIT 1',
            [process_name, "PENDING"])
        row = cursor.fetchone()
        cursor.close()
        if row:
            return SyncSession(id=UUID(row[0]), process_name=row[1], start_time=row[2], end_time=row[3], initial_count=row[4], status=ProcessStatus(row[5]), duration_seconds=row[6])
        return None

    def get_recent_sessions(self, process_name: str, limit: int = 10) -> List[SyncSession]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, process_name, start_time, end_time, initial_count, status, duration_seconds FROM "CL".sync_sessions WHERE process_name = %s ORDER BY start_time DESC LIMIT %s',
            [process_name, limit])
        rows = cursor.fetchall()
        cursor.close()
        return [SyncSession(id=UUID(r[0]), process_name=r[1], start_time=r[2], end_time=r[3], initial_count=r[4], status=ProcessStatus(r[5]), duration_seconds=r[6]) for r in rows]


class PostgresSnapshotRepository:
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None or cls._connection.closed:
            pwd = os.getenv("POSTGRES_PASSWORD", "") or ""
            cls._connection = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "10.40.3.170"),
                port=os.getenv("POSTGRES_PORT", "5433"),
                database=os.getenv("POSTGRES_DB", "Monitores"),
                user=os.getenv("POSTGRES_USER", "user_monitores_app"),
                password=pwd)
            cls._connection.autocommit = True
        return cls._connection

    def save_snapshot(self, snapshot: MetricSnapshot) -> MetricSnapshot:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO "CL".sync_snapshots (session_id, captured_at, current_count) VALUES (%s, %s, %s) RETURNING id',
            [str(snapshot.session_id), snapshot.captured_at, snapshot.current_count])
        row = cursor.fetchone()
        cursor.close()
        if row:
            snapshot.id = row[0]
        return snapshot

    def get_snapshots_by_session(self, session_id: UUID) -> List[MetricSnapshot]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, session_id, captured_at, current_count FROM "CL".sync_snapshots WHERE session_id = %s ORDER BY captured_at ASC', [str(session_id)])
        rows = cursor.fetchall()
        cursor.close()
        return [MetricSnapshot(id=row[0], session_id=UUID(row[1]), captured_at=row[2], current_count=row[3]) for row in rows]