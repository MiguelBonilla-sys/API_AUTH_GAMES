# Dockerfile para Railway
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verificar que psycopg2 esté instalado
RUN python -c "import psycopg2; print('psycopg2 instalado correctamente')"

# Copiar código fuente
COPY . .

# Verificar configuración de base de datos
RUN python check_db.py

# Hacer ejecutable el script de inicio
RUN chmod +x start.sh

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import httpx; import os; httpx.get(f'http://localhost:{os.getenv(\"PORT\", \"8000\")}/health', timeout=10)"

# Comando de inicio
CMD ["./start.sh"]
