#!/bin/bash

# Script de inicio para Railway
echo "🚀 Iniciando API Auth Gateway..."

# Configurar variables de entorno por defecto
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}
export ENVIRONMENT=${ENVIRONMENT:-production}
export DEBUG=${DEBUG:-false}

# Corregir URL de base de datos si es necesario
if [[ -n "$DATABASE_URL" && "$DATABASE_URL" == postgresql://* && "$DATABASE_URL" != *"+asyncpg"* ]]; then
    echo "🔧 Corrigiendo URL de base de datos..."
    export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg:\/\/}"
    echo "✅ URL corregida para usar asyncpg"
fi

echo "📊 Configuración:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Environment: $ENVIRONMENT"
echo "   Debug: $DEBUG"

# Verificar que PORT sea un número válido
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ Error: PORT debe ser un número válido. Valor actual: $PORT"
    exit 1
fi

# Verificar que PORT esté en el rango válido
if [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "❌ Error: PORT debe estar entre 1 y 65535. Valor actual: $PORT"
    exit 1
fi

echo "✅ Puerto válido: $PORT"

# Iniciar la aplicación
echo "🚀 Iniciando Gunicorn..."
exec gunicorn app:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind $HOST:$PORT \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
