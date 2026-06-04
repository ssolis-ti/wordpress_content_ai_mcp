# =================================================================
# Dockerfile - WordPress AI Content System (wp_mcp_content_ai)
# =================================================================

FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc en disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evitar que Python almacene en búfer stdout/stderr (importante para streaming de logs)
ENV PYTHONUNBUFFERED=1
# Forzar codificación UTF-8 para salida de consola
ENV PYTHONIOENCODING=utf-8

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requerimientos de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY app/ ./app/
COPY bridge/ ./bridge/
COPY data/ ./data/
COPY portero/ ./portero/

# Exponer el volumen de datos para persistencia local de posts y resultados
VOLUME ["/app/data"]

# Comando por defecto: ejecutar el servidor MCP sobre stdio
CMD ["python", "bridge/mcp_server.py"]
