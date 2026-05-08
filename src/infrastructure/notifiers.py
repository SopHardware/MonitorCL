from __future__ import annotations
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests

from ..domain.entities import ProcessStatus, format_duration
from ..domain.entities import ProcessMetrics

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Notificador para enviar reportes a Slack"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.last_alert_time: Optional[datetime] = None

    def send_status_report(
        self,
        process_metrics: Dict[str, ProcessMetrics],
        interval_minutes: int = 10
    ) -> bool:
        """Envía reporte con KPIs a Slack"""
        try:
            blocks = self._build_kpi_blocks(process_metrics, interval_minutes)
            payload = {"blocks": blocks}
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Reporte KPI enviado a Slack")
                return True
            else:
                logger.error(f"Error Slack: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Excepción Slack: {str(e)}")
            return False

    def send_critical_alert(
        self,
        process_key: str,
        host: str,
        error: str,
        metrics: ProcessMetrics
    ) -> bool:
        """Envía alerta crítica cuando proceso falla 3+ veces"""
        try:
            # Evitar spam de alertas (mínimo 30 min entre alertas)
            if self.last_alert_time:
                elapsed = (datetime.now() - self.last_alert_time).total_seconds()
                if elapsed < 1800:  # 30 minutos
                    logger.info(f"Alerta crítica suprimida (demasiado pronto)")
                    return False
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 ALERTA CRÍTICA - Fallo en Proceso",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Proceso:*\n{process_key}"},
                        {"type": "mrkdwn", "text": f"*Host:*\n{host}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error:*\n```{error}```"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
                    ]
                }
            ]
            
            payload = {"blocks": blocks}
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_alert_time = datetime.now()
                logger.info(f"Alerta crítica enviada para {process_key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error enviando alerta crítica: {str(e)}")
            return False

    def _build_kpi_blocks(
        self,
        process_metrics: Dict[str, ProcessMetrics],
        interval_minutes: int
    ) -> List[Dict[str, Any]]:
        """Construye bloques con KPIs completos"""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🔄 Monitor de Sincronización", "emoji": True}
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
                ]
            },
            {"type": "divider"}
        ]
        
        critical_processes = []
        
        for process_key, metrics in process_metrics.items():
            # Obtener último count - prioridad: session.initial_count > snapshots > 0
            last_count = 0
            if metrics.session and metrics.session.is_active():
                # Sesión activa: usar initial_count
                last_count = metrics.session.initial_count
            elif metrics.snapshots:
                # Sin sesión activa: obtener del último snapshot
                last_count = metrics.snapshots[-1].current_count
            
            status = "🟢 OK"
            duration = "-"
            
            if metrics.error_count > 0:
                status = "❌ Error"
            elif metrics.session and not metrics.session.is_active():
                status = "✅ Completado"
                if metrics.session.duration_seconds:
                    duration = format_duration(metrics.session.duration_seconds)
            elif metrics.session and metrics.session.is_active():
                status = "⏳ En proceso"
                duration = metrics.get_duration()
            
            # Verificar fallos críticos
            if metrics.has_critical_failure():
                critical_processes.append(process_key)
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{metrics.process_key}*\n📊 {last_count:,} | {status} | ⏱️ {duration}"
                }
            })
        
        # Summary de errores
        if critical_processes:
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🚨 *FALLOS CRÍTICOS:* {', '.join(critical_processes)}"
                }
            })
        
        # Footer
        blocks.extend([
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"⏱️ Intervalo: {interval_minutes} min | Horario: 18:30-06:00"}
                ]
            }
        ])
        
        return blocks