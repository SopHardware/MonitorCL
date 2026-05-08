from __future__ import annotations
import unittest
from datetime import datetime
from uuid import UUID

from src.domain.entities import SyncSession, MetricSnapshot, ProcessStatus


class TestDomainEntities(unittest.TestCase):
    """Tests para las entidades de dominio"""

    def test_sync_session_creation(self):
        """Test de creación de una sesión de sincronización"""
        session = SyncSession(
            process_name="TEST_PROCESS",
            start_time=datetime.now(),
            initial_count=5
        )
        
        self.assertIsInstance(session.id, UUID)
        self.assertEqual(session.process_name, "TEST_PROCESS")
        self.assertEqual(session.initial_count, 5)
        self.assertEqual(session.status, ProcessStatus.PENDING)
        self.assertIsNone(session.end_time)
        self.assertIsNone(session.duration_seconds)

    def test_sync_session_close(self):
        """Test de cierre de sesión de sincronización"""
        start_time = datetime.now()
        session = SyncSession(
            process_name="TEST_PROCESS",
            start_time=start_time,
            initial_count=10
        )
        
        # Cerrar sesión
        end_time = datetime.now()
        session.close_session(end_time)
        
        self.assertEqual(session.status, ProcessStatus.COMPLETED)
        self.assertEqual(session.end_time, end_time)
        self.assertIsNotNone(session.duration_seconds)
        self.assertGreaterEqual(session.duration_seconds, 0)

    def test_metric_snapshot_creation(self):
        """Test de creación de un snapshot métrico"""
        session_id = UUID('12345678-1234-5678-1234-567812345678')
        snapshot = MetricSnapshot(
            session_id=session_id,
            captured_at=datetime.now(),
            current_count=42
        )
        
        self.assertEqual(snapshot.session_id, session_id)
        self.assertEqual(snapshot.current_count, 42)
        self.assertEqual(snapshot.id, 0)  # Valor por defecto


if __name__ == '__main__':
    unittest.main()
