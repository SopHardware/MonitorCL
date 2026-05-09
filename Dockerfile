FROM python:3.11-slim-bullseye

# Instalar dependencias del sistema incluyendo drivers ODBC
RUN apt-get update && apt-get install -y \
    gnupg2 \
    curl \
    apt-transport-https \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la aplicación
WORKDIR /app

# Copiar archivos de requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ ./src/
COPY config.py ./

# Crear directorio para logs
RUN mkdir -p /app/logs

# Exponer puertos (si fuera necesario)
# EXPOSE 8000

# Comando de entrada
CMD ["python", "-m", "src.entrypoints.worker"]
