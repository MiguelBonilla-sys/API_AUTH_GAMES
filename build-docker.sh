#!/bin/bash

# Script para construir Docker con diferentes opciones

echo "🐳 Constructor de Docker para Railway"
echo "======================================"

# Verificar que Docker esté disponible
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

echo "📋 Opciones disponibles:"
echo "1. Dockerfile principal (con script de inicio)"
echo "2. Dockerfile alternativo (comando directo)"
echo "3. Dockerfile simplificado"
echo ""

read -p "Selecciona una opción (1-3): " choice

case $choice in
    1)
        echo "🔨 Construyendo con Dockerfile principal..."
        docker build -t api-auth-gateway -f Dockerfile .
        ;;
    2)
        echo "🔨 Construyendo con Dockerfile alternativo..."
        docker build -t api-auth-gateway -f Dockerfile.alt .
        ;;
    3)
        echo "🔨 Construyendo con Dockerfile simplificado..."
        docker build -t api-auth-gateway -f Dockerfile.simple .
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo "✅ Imagen construida exitosamente"
    echo "🚀 Para ejecutar: docker run -p 8000:8000 api-auth-gateway"
    echo "🔍 Para ver logs: docker logs <container_id>"
    echo "🏥 Para health check: curl http://localhost:8000/health"
else
    echo "❌ Error construyendo la imagen"
    exit 1
fi
