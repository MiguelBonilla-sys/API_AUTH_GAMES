#!/bin/bash

# Script de build para Docker
echo "🐳 Construyendo imagen Docker..."

# Construir imagen
docker build -t api-auth-gateway .

echo "✅ Imagen construida exitosamente"
echo "🚀 Para ejecutar: docker run -p 8000:8000 api-auth-gateway"
echo "🔍 Para ver logs: docker logs <container_id>"
echo "🏥 Para health check: curl http://localhost:8000/health"
