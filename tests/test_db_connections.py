from __future__ import annotations
import os
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
import pyodbc

from src.infrastructure.adapters import SqlServerAdapter
from src.shared.utils import get_mssql_connection_string


class TestSqlServerAdapter(unittest.TestCase):
    """Tests para el SqlServerAdapter"""

    def setUp(self):
        """Configuración inicial de tests"""
        self.connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=192.168.3.66,1433;"
            "DATABASE=GAINS;"
            "UID=testuser;"
            "PWD=testpass;"
        )
        self.adapter = SqlServerAdapter(self.connection_string)

    def test_adapter_initialization(self):
        """Test que el adapter se inicializa correctamente"""
        self.assertEqual(self.adapter.connection_string, self.connection_string)

    def test_connection_string_contains_database(self):
        """Test que el connection string incluye la database"""
        self.assertIn("DATABASE=GAINS", self.connection_string)

    @patch('src.infrastructure.adapters.pyodbc.connect')
    def test_test_connection_success(self, mock_connect):
        """Test de conexión exitosa"""
        mock_cursor = MagicMock()
        
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = self.adapter.test_connection()

        self.assertTrue(result)

    @patch('src.infrastructure.adapters.pyodbc.connect')
    def test_test_connection_failure(self, mock_connect):
        """Test de conexión fallida"""
        mock_connect.side_effect = Exception("Connection failed")

        result = self.adapter.test_connection()

        self.assertFalse(result)


class TestConnectionStringBuilder(unittest.TestCase):
    """Tests para el builder de connection string"""

    def test_get_mssql_connection_string_with_database(self):
        """Test que构建 connection string con database específica"""
        conn_str = get_mssql_connection_string(
            host="192.168.3.66",
            user="testuser",
            password="testpass",
            database="GAINS",
            port=1433,
            timeout=30
        )

        self.assertIn("SERVER=192.168.3.66,1433", conn_str)
        self.assertIn("DATABASE=GAINS", conn_str)
        self.assertIn("UID=testuser", conn_str)
        self.assertIn("PWD=testpass", conn_str)
        self.assertIn("Timeout=30", conn_str)

    def test_get_mssql_connection_string_default_master(self):
        """Test que usa master por defecto cuando no se especifica database"""
        conn_str = get_mssql_connection_string(
            host="192.168.3.66",
            user="testuser",
            password="testpass"
        )

        self.assertIn("DATABASE=master", conn_str)

    def test_get_mssql_connection_string_custom_port(self):
        """Test que usa puerto personalizado"""
        conn_str = get_mssql_connection_string(
            host="192.168.3.66",
            user="testuser",
            password="testpass",
            database="TestDB",
            port=1434
        )

        self.assertIn("SERVER=192.168.3.66,1434", conn_str)


class TestDatabaseConfiguration(unittest.TestCase):
    """Tests para verificar la configuración de bases de datos"""

    def test_database_config_fields_exist(self):
        """Verifica que los campos de database existan en Settings"""
        with patch.dict(os.environ, {
            "APP_NAME": "SyncSentinel",
            "APP_ENV": "test",
            "MSSQL_USER": "testuser",
            "MSSQL_PASS": "testpass",
            "HOST_GAINS": "192.168.3.66",
            "HOST_REPLICA": "192.168.3.83",
            "HOST_EPICOR": "192.168.3.72",
            "HOST_CL": "192.168.20.19",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "db_metrics",
            "SLACK_WEBHOOK_URL": "https://hooks.slack.com/test"
        }):
            from config import Settings
            settings = Settings()
            
            self.assertIn("MSSQL_DB_GAINS", settings.model_fields)
            self.assertIn("MSSQL_DB_REPLICA", settings.model_fields)
            self.assertIn("MSSQL_DB_EPICOR", settings.model_fields)
            self.assertIn("MSSQL_DB_CL", settings.model_fields)


@unittest.skipUnless(
    os.environ.get("RUN_INTEGRATION_TESTS", "0") == "1",
    "Integration tests deshabilitados por defecto"
)
class TestSqlServerIntegration(unittest.TestCase):
    """Tests de integración reales a las bases de datos"""
    
    @classmethod
    def setUpClass(cls):
        """Carga configuración real"""
        from config import Settings
        cls.settings = Settings()

    def test_gains_connection(self):
        """Test de conexión a GAINS"""
        conn_str = get_mssql_connection_string(
            host=self.settings.HOST_GAINS,
            user=self.settings.MSSQL_USER,
            password=self.settings.MSSQL_PASS,
            database=self.settings.MSSQL_DB_GAINS
        )
        adapter = SqlServerAdapter(conn_str)
        
        result = adapter.test_connection()
        self.assertTrue(result, "No se pudo conectar a GAINS")

    def test_replica_connection(self):
        """Test de conexión a Réplica"""
        conn_str = get_mssql_connection_string(
            host=self.settings.HOST_REPLICA,
            user=self.settings.MSSQL_USER,
            password=self.settings.MSSQL_PASS,
            database=self.settings.MSSQL_DB_REPLICA
        )
        adapter = SqlServerAdapter(conn_str)
        
        result = adapter.test_connection()
        self.assertTrue(result, "No se pudo conectar a Réplica")

    def test_epicor_connection(self):
        """Test de conexión a Epicor"""
        conn_str = get_mssql_connection_string(
            host=self.settings.HOST_EPICOR,
            user=self.settings.MSSQL_USER,
            password=self.settings.MSSQL_PASS,
            database=self.settings.MSSQL_DB_EPICOR
        )
        adapter = SqlServerAdapter(conn_str)
        
        result = adapter.test_connection()
        self.assertTrue(result, "No se pudo conectar a Epicor")

    def test_cl_connection(self):
        """Test de conexión a CL"""
        conn_str = get_mssql_connection_string(
            host=self.settings.HOST_CL,
            user=self.settings.MSSQL_USER,
            password=self.settings.MSSQL_PASS,
            database=self.settings.MSSQL_DB_CL
        )
        adapter = SqlServerAdapter(conn_str)
        
        result = adapter.test_connection()
        self.assertTrue(result, "No se pudo conectar a CL")


import os

if __name__ == '__main__':
    unittest.main()