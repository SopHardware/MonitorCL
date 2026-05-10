# Deploy con Portainer

Esta guía describe cómo desplegar **SyncSentinel** usando **Portainer** en un servidor con Docker.

## Requisitos Previos

| Requisito | Descripción |
|-----------|-------------|
| Docker | Versión 20.10+ |
| Portainer | Versión 2.0+ |
| SQL Server | Acceso a los 4 servidores |
| Slack | Webhook configurado |

## Paso 1: Preparar el Entorno

### 1.1 Crear la red de Docker (si no existe)

```bash
docker network create syncsentinel-net
```

### 1.2 Variables de Entorno

Las variables de entorno se configuran directamente en Portainer (ver sección 2.3). No es necesario crear un archivo `.env` local.

---

## Paso 2: Deploy con Portainer

### 2.1 Acceder a Portainer

1. Abrir navegador: `http://tu-servidor:9000`
2. Iniciar sesión

### 2.2 Crear Stack

1. Ir a **Stacks** → **Add stack**
2. Nombre: `syncsentinel`

### 2.3 Configurar Stack

**Opción A: Usar Web Editor**

1. Pegar el contenido del archivo `docker-compose.yml` del repositorio
2. Ir a la sección **Environment** (abajo del editor)
3. Agregar las siguientes variables de entorno:

| Variable | Valor |
|----------|-------|
| APP_NAME | SyncSentinel |
| APP_ENV | prod |
| MONITOR_START_TIME | 18:30 |
| MONITOR_END_TIME | 06:00 |
| CHECK_INTERVAL_SECONDS | 600 |
| MSSQL_USER | (tu usuario SQL) |
| MSSQL_PASS | (tu contraseña SQL) |
| HOST_GAINS | 10.40.3.66 |
| HOST_REPLICA | 10.40.3.83 |
| HOST_EPICOR | 10.40.3.72 |
| HOST_CL | 192.168.20.19 |
| MSSQL_DB_GAINS | Intermedia |
| MSSQL_DB_REPLICA | ReplicationDataBase |
| MSSQL_DB_EPICOR | EpicorERP |
| MSSQL_DB_CL | SAS1115 |
| POSTGRES_USER | user_monitores_app |
| POSTGRES_PASSWORD | (tu contraseña PostgreSQL) |
| POSTGRES_HOST | 10.40.3.170 |
| POSTGRES_PORT | 5433 |
| POSTGRES_DB | Monitores |
| POSTGRES_SCHEMA | CL |
| SLACK_WEBHOOK_URL | (tu webhook de Slack) |
| START_DATE_DAYS_BACK | 30 |

4. Click en **Deploy the stack**

**Opción B: Usar Git Repository**

1. Repository URL: `https://github.com/SopHardware/MonitorCL`
2. Reference: `main` o `fix/gitguardian-scan-issues`
3. Build: `Dockerfile`
4. En la sección **Environment**, agregar las variables de la tabla anterior

### 2.4 Desplegar

1. Click **Deploy the stack**
2. Esperar a que complete

---

## Paso 3: Verificar Deployment

### 3.1 Verificar Contenedor

1. Ir a **Containers**
2. Buscar `syncsentinel`
3. Verificar estado: **Running** (verde)

### 3.2 Verificar Logs

1. Click en `syncsentinel`
2. Ir a **Logs**
3. Buscar mensajes de inicio:

```
Inicializando componentes...
Conectado a GAINS
Conectado a REPLICA
Conectado a EPICOR
Componentes inicializados
Monitoreando 5 procesos...
```

### 3.3 Verificar en Slack

Ejecutar manualmente para probar:

```bash
# Entrar al contenedor
docker exec -it syncsentinel bash

# Ejecutar worker
python -m src.entrypoints.worker
```

Debería llegar mensaje a Slack con KPIs.

---

## Paso 4: Configurar Healthcheck

### 4.1 Healthcheck en Portainer

1. Ir al contenedor `syncsentinel`
2. Editar
3. Agregar healthcheck:

```bash
#Dentro del contenedor
python -c "import sys; sys.exit(0)"
```

### 4.2 Reinicio Automático

En la configuración del stack, Ya está configurado:

```yaml
restart: unless-stopped
```

---

## Paso 5: Monitoreo

### 5.1 Ver métricas del contenedor

1. Ir a **Container Stats**
2. Observar:
   - CPU usage
   - Memory usage
   - Network I/O

### 5.2 Ver logs en tiempo real

```bash
# Desde terminal
docker logs -f syncsentinel

# O desde Portainer
Container → Logs → Follow
```

---

## Actualización del Deployment

### Actualizar a nueva versión

1. Ir a **Stacks**
2. Editar `syncsentinel`
3. Cambiar image tag o repository reference
4. Click **Update stack**

---

## Troubleshooting

### Problema: Container no inicia

**Causa**: Faltan variables de entorno

**Solución**: Verificar que todas las variables estén configuradas en Portainer:
```bash
docker exec syncsentinel env | grep -E "(MSSQL|POSTGRES|SLACK)"
```

### Problema: No conecta a SQL Server

**Causa**: Red no configurada

**Solución**:
```bash
docker network connect syncsentinel-net syncsentinel
```

### Problema: No llega a Slack

**Causa**: Webhook incorrecto

**Solución**: Verificar variable `SLACK_WEBHOOK_URL` en contenedor:
```bash
docker exec syncsentinel env | grep SLACK
```

---

## Variables de Entorno en Portainer

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `APP_NAME` | Nombre de app | SyncSentinel |
| `MONITOR_START_TIME` | Inicio ventana | 18:30 |
| `MONITOR_END_TIME` | Fin ventana | 06:00 |
| `CHECK_INTERVAL_SECONDS` | Intervalo (seg) | 600 |
| `MSSQL_USER` | Usuario SQL | MonitorCL |
| `MSSQL_PASS` | Contraseña SQL | ***** |
| `HOST_GAINS` | IP GAINS | 10.40.3.66 |
| `HOST_REPLICA` | IP Réplica | 10.40.3.83 |
| `HOST_EPICOR` | IP Epicor | 10.40.3.72 |
| `HOST_CL` | IP CL | 192.168.20.19 |
| `SLACK_WEBHOOK_URL` | Webhook | https://hooks.slack.com/... |

---

## Consultas

- **Dashboard**: No disponible (futuro)
- **Historial**: No disponible (futuro)
- **Métricas persistidas**: No disponible (PostgreSQL pendiente)