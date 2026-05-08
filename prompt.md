# PROMPT MAESTRO: PROYECTO SYNC-SENTINEL ENTERPRISE

## 🎯 1. IDENTIDAD Y OBJETIVO
Actúa como un **Arquitecto de Software Senior** especializado en Python. Debes diseñar y codificar una solución de monitoreo de sincronización de bases de datos denominada **"SyncSentinel"**. El sistema debe ser un servicio productivo, resiliente, auditable y bajo los estándares de **Clean Architecture**.

## 🏛️ 2. ESTÁNDAR ARQUITECTÓNICO Y PATRONES
Aplica estrictamente **Clean Architecture**, **DDD** (Domain-Driven Design) y **SOLID**.
- **Estructura de Directorios:**
  - `src/domain/`: Entidades (`SyncSession`, `MetricSnapshot`), Value Objects e interfaces de repositorios.
  - `src/application/`: Casos de uso (`ProcessMonitor`, `SessionManager`, `NotificationService`).
  - `src/infrastructure/`: Adaptadores de SQL Server (`pyodbc`), Repositorio PostgreSQL (`SQLAlchemy`), Notificador de Slack y Scheduler.
  - `src/entrypoints/`: Punto de entrada principal (Worker en Docker).
  - `src/shared/`: Logging estructurado, excepciones de dominio y utilidades.
- **Patrones Obligatorios:** Repository Pattern, Unit of Work, Strategy (para los queries), Factory, Adapter y Dependency Injection.

## 📋 3. LÓGICA DE NEGOCIO Y REGLAS (WINDOW & KPI)
El sistema monitorea colas de sincronización entre múltiples nodos SQL Server.
1. **Ventana de Operación (Configurable):**
   - **6:30 PM:** Inicio de "Health Checks" y disponibilidad de red.
   - **7:00 PM:** Inicio de validaciones de datos y conteo de registros.
   - **05:00 AM:** Cierre de ventana y modo standby.
2. **Intervalo:** Ejecución cada 3 minutos.
3. **Cálculo de "Tiempo Total" (Queue Drain Time):**
   - Si `count > 0` y no hay sesión activa: Crear `SyncSession` con `start_time = NOW()`.
   - Si `count == 0` y hay sesión activa: Cerrar sesión, calcular duración total y reportar.
4. **Resiliencia:** El fallo en un nodo (ej. 3.66) no debe detener el monitoreo de los demás. Usar `tenacity` para reintentos con backoff exponencial (máx 3 intentos).

## 🔍 4. QUERIES DE EXTRACCIÓN (Basados en "Aprobaciones")
Implementar los siguientes adaptadores con SQL Auth:
- **GAINS (3.66):** `SELECT COUNT(DISTINCT(IdRegistro)) FROM PO_Traspasos WHERE ExportStatus = 0`
- **Réplica (3.83):** Conteo en `ReplicateData` filtrando por `DocumentName = 'TransferOrderGains'` y lógica de hora nocturna (post 19:00 hrs).
- **Cola de Material (20.19):** Conteo en `BXCJ_ConsolidadoEncabezadoCLON` con sus respectivos Joins y filtros de estatus.
- **Epicor (3.72):** Validación en `ICE.UD24` donde `Character01 <> 'Finalizado'`.
- **Embarques (20.19):** Conteo de folios en `BXCJ_ConsolidadoEncabezadoCLON` validando estatus de exportación.

## 📊 5. OBSERVABILIDAD Y NOTIFICACIONES
### Slack Block Kit Template:
Generar un mensaje estructurado con las siguientes secciones:
- **Header:** 🟢 Monitor de Sincronización Nocturna
- **Context:** 🕒 Última actualización: `YYYY-MM-DD HH:mm:SS`
- **Divider**
- **Section (Loop):** `*Proceso:* {nombre}` | `*Estatus:* {Pendiente/Completado}` | `*Registros:* {count}` | `*Tiempo:* {duracion_total}`
- **Footer:** 📝 Correlation ID: `{uuid}`
- **Alerta Crítica:** Si un nodo falla persistentemente tras 3 reintentos: `🚨 ERROR: Nodo {IP} fuera de línea.`

### Esquema PostgreSQL (Local Metrics):
- **Tabla `sync_sessions`:** `id (UUID)`, `process_name`, `start_time`, `end_time`, `initial_count`, `status (Enum)`.
- **Tabla `sync_snapshots`:** `id (BigInt)`, `session_id (FK)`, `captured_at`, `current_count`.
- *Uso de SQLAlchemy + Alembic para migraciones.*

## ⚙️ 6. INFRAESTRUCTURA Y CONFIGURACIÓN
### Archivo .env (Cargar vía Pydantic Settings):
```env
APP_NAME=SyncSentinel
APP_ENV=prod
CHECK_INTERVAL_SECONDS=180
MONITOR_START_TIME=18:30
VALIDATION_START_TIME=19:00
MONITOR_END_TIME=05:00
MSSQL_USER=...
MSSQL_PASS=...
HOST_GAINS=192.168.3.66
HOST_REPLICA=192.168.3.83
HOST_EPICOR=192.168.3.72
HOST_CL=192.168.20.19
DATABASE_URL=postgresql://postgres:pass@db:5432/db_metrics
SLACK_WEBHOOK_URL=...
```
### Docker:
- **Imagen:** `python:3.11-slim-bullseye`.
- **Drivers:** Instalar `msodbcsql17` o `msodbcsql18` y `unixodbc-dev`.
- **Compose:** Incluir el servicio de la app y la base de datos PostgreSQL.

## 🧪 7. CALIDAD Y TESTING
- **Pytest:** Mínimo 80% de cobertura.
- **Unit Tests:** Probar lógica de tiempo y mapeo de queries.
- **Mocks:** Simular respuestas de SQL Server y Slack.
- **Logging:** Formato JSON estructurado con rotación.

**GENERA EL PROYECTO SIGUIENDO ESTAS ESPECIFICACIONES.**