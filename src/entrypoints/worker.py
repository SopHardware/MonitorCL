from __future__ import annotations
import asyncio
import logging
import signal
from datetime import datetime, time
from typing import Dict, List, Optional

from ..domain.entities import ProcessMetrics, ProcessStatus
from ..infrastructure.adapters import SqlServerAdapter
from ..infrastructure.notifiers import SlackNotifier
from ..shared.logging import setup_logging
from ..shared.query_loader import get_process_query
from ..shared.utils import get_mssql_connection_string
from config import Settings

setup_logging()
logger = logging.getLogger(__name__)


class SyncSentinelWorker:
    """Worker principal con Session Management y KPIs"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self.sql_adapters: Dict[str, SqlServerAdapter] = {}
        self.slack_notifier: Optional[SlackNotifier] = None
        
        # Métricas en memoria por proceso
        self.process_metrics: Dict[str, ProcessMetrics] = {}
        
        start_date_days = settings.START_DATE_DAYS_BACK
        
        self.processes = {
            "GAINS": {
                "name": "Aprobaciones GAINS → Réplica",
                "query": get_process_query("GAINS_3.66", start_date_days),
                "host": settings.HOST_GAINS,
                "database": settings.MSSQL_DB_GAINS
            },
            "REPLICA": {
                "name": "Aprobaciones Réplica → Epicor",
                "query": get_process_query("REPLICA_3.83", start_date_days),
                "host": settings.HOST_REPLICA,
                "database": settings.MSSQL_DB_REPLICA
            },
            "MATERIAL_CL": {
                "name": "Cola de Material CL → Réplica",
                "query": get_process_query("MATERIAL_CL_REPLICA", start_date_days),
                "host": settings.HOST_CL,
                "database": settings.MSSQL_DB_CL
            },
            "EPICOR": {
                "name": "Estatus Epicor",
                "query": get_process_query("EPICOR_3.72", start_date_days),
                "host": settings.HOST_EPICOR,
                "database": settings.MSSQL_DB_EPICOR
            },
            "EMBARQUES_CL": {
                "name": "Embarques CL → Réplica",
                "query": get_process_query("EMBARQUES_CL_REPLICA", start_date_days),
                "host": settings.HOST_CL,
                "database": settings.MSSQL_DB_CL
            }
        }
        
        # Inicializar métricas
        for process_key, process_info in self.processes.items():
            self.process_metrics[process_key] = ProcessMetrics(
                process_key=process_info["name"]
            )

    async def start(self) -> None:
        """Inicia el worker"""
        logger.info("Iniciando SyncSentinel Worker...")
        self.running = True
        
        try:
            await self._initialize_components()
            await self._main_loop()
        except Exception as e:
            logger.error(f"Error en worker: {e}")
        finally:
            await self.stop()

    async def _initialize_components(self) -> None:
        """Inicializa los componentes necesarios"""
        logger.info("Inicializando componentes...")
        
        for process_key, process_info in self.processes.items():
            connection_string = get_mssql_connection_string(
                host=process_info["host"],
                user=self.settings.MSSQL_USER,
                password=self.settings.MSSQL_PASS,
                database=process_info["database"]
            )
            self.sql_adapters[process_key] = SqlServerAdapter(connection_string)
            logger.info(f"Conectado a {process_key}")
        
        self.slack_notifier = SlackNotifier(self.settings.SLACK_WEBHOOK_URL)
        logger.info("Componentes inicializados")

    async def _main_loop(self) -> None:
        """Loop principal con scheduler"""
        interval_seconds = self.settings.CHECK_INTERVAL_SECONDS
        logger.info(f"Iniciando loop - Horario: 18:30-06:00, Intervalo: {interval_seconds}s")
        
        while self.running:
            try:
                now = datetime.now().time()
                monitor_start = time.fromisoformat(self.settings.MONITOR_START_TIME)
                monitor_end = time.fromisoformat(self.settings.MONITOR_END_TIME)
                
                # Window Cruzando medianoche
                if monitor_start <= monitor_end:
                    in_window = monitor_start <= now < monitor_end
                else:
                    in_window = now >= monitor_start or now < monitor_end
                
                if not in_window:
                    logger.info(f"Fuera de horario. Hora: {now}. Próximo ciclo en {interval_seconds}s")
                    await asyncio.sleep(interval_seconds)
                    continue
                
                await self._monitor_processes()
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error en loop: {e}")
                await asyncio.sleep(interval_seconds)

    async def _monitor_processes(self) -> None:
        """Ejecuta el monitoreo con lifecycle de sesiones"""
        logger.info(f"Monitoreando {len(self.processes)} procesos...")
        
        for process_key, process_info in self.processes.items():
            metrics = self.process_metrics[process_key]
            
            try:
                adapter = self.sql_adapters[process_key]
                query = process_info["query"]
                count = adapter.execute_count_query(query)
                
                # Resetear errores en éxito
                metrics.reset_errors()
                
                # Agregar snapshot
                metrics.add_snapshot(count)
                
                # Session lifecycle
                if count > 0 and not metrics.session:
                    # Iniciar nueva sesión
                    metrics.start_session(count)
                    logger.info(f"  {process_key}: SESIÓN INICIADA (count={count})")
                elif count == 0 and metrics.session and metrics.session.is_active():
                    # Cerrar sesión
                    closed_session = metrics.close_session()
                    logger.info(f"  {process_key}: SESIÓN CERRADA (duration={closed_session.duration_seconds}s)")
                
                logger.info(f"  {process_key}: count={count}, duration={metrics.get_duration()}")
                
            except Exception as e:
                # Incrementar error
                metrics.increment_error(str(e))
                logger.error(f"  {process_key}: ERROR ({metrics.error_count}/3) - {str(e)[:50]}")
                
                # Verificar fallo crítico
                if metrics.has_critical_failure() and self.slack_notifier:
                    self.slack_notifier.send_critical_alert(
                        process_key=process_key,
                        host=process_info["host"],
                        error=str(e),
                        metrics=metrics
                    )
        
        logger.info("Ciclo completado")
        
        # Enviar reporte con KPIs
        interval_minutes = self.settings.CHECK_INTERVAL_SECONDS // 60
        if self.slack_notifier:
            self.slack_notifier.send_status_report(
                process_metrics=self.process_metrics,
                interval_minutes=interval_minutes
            )
            logger.info("Reporte KPI enviado a Slack")

    async def stop(self) -> None:
        """Detiene el worker"""
        logger.info("Deteniendo worker...")
        self.running = False
        
        # Cerrar sesiones abiertas
        for process_key, metrics in self.process_metrics.items():
            if metrics.session and metrics.session.is_active():
                closed = metrics.close_session()
                logger.info(f"  {process_key}: Sesión cerrada al stop: {closed.duration_seconds}s")
        
        logger.info("Worker detenido")

    async def run_single_cycle(self) -> None:
        """Ejecuta un ciclo para testing"""
        await self._initialize_components()
        await self._monitor_processes()


if __name__ == "__main__":
    from config import settings as app_settings
    
    async def main():
        worker = SyncSentinelWorker(app_settings)
        await worker.start()  # Usa start() para respetar el scheduler
    
    asyncio.run(main())