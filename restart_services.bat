@echo off
echo 🔧 Verificando configuración de Docker Compose...

REM Detener servicios existentes
echo ⏹️ Deteniendo servicios...
docker-compose down

REM Limpiar contenedores e imágenes huérfanas
echo 🧹 Limpiando contenedores...
docker system prune -f

REM Reconstruir y levantar los servicios
echo 🏗️ Reconstruyendo y levantando servicios...
docker-compose up --build -d

REM Esperar a que los servicios estén listos
echo ⏳ Esperando que los servicios estén listos...
timeout /t 10 /nobreak

REM Verificar el estado de los servicios
echo 📊 Estado de los servicios:
docker-compose ps

REM Verificar logs de la aplicación
echo 📋 Logs de la aplicación:
docker-compose logs app --tail=20

REM Verificar logs de Redis
echo 📋 Logs de Redis:
docker-compose logs redis --tail=10

REM Probar la conectividad
echo 🧪 Probando la API...
curl -s http://localhost:8000/ 2>nul || echo ❌ Error al conectar con la API

echo ✅ Verificación completada!
pause
