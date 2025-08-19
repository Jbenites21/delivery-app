#!/bin/bash
# Script para verificar y reiniciar los servicios

echo "🔧 Verificando configuración de Docker Compose..."

# Detener servicios existentes
echo "⏹️ Deteniendo servicios..."
docker-compose down

# Limpiar contenedores e imágenes huérfanas
echo "🧹 Limpiando contenedores..."
docker system prune -f

# Reconstruir y levantar los servicios
echo "🏗️ Reconstruyendo y levantando servicios..."
docker-compose up --build -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando que los servicios estén listos..."
sleep 10

# Verificar el estado de los servicios
echo "📊 Estado de los servicios:"
docker-compose ps

# Verificar logs de la aplicación
echo "📋 Logs de la aplicación:"
docker-compose logs app --tail=20

# Verificar logs de Redis
echo "📋 Logs de Redis:"
docker-compose logs redis --tail=10

# Probar la conectividad
echo "🧪 Probando la API..."
curl -s http://localhost:8000/ | python -m json.tool 2>/dev/null || echo "❌ Error al conectar con la API"

echo "✅ Verificación completada!"
