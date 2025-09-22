@echo off
echo 🐳 Construyendo imagen Docker...

REM Construir imagen
docker build -t api-auth-gateway .

if %errorlevel% equ 0 (
    echo ✅ Imagen construida exitosamente
    echo 🚀 Para ejecutar: docker run -p 8000:8000 api-auth-gateway
    echo 🔍 Para ver logs: docker logs ^<container_id^>
    echo 🏥 Para health check: curl http://localhost:8000/health
) else (
    echo ❌ Error construyendo la imagen
    exit /b 1
)
