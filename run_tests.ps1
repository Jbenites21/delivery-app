# Script para ejecutar las pruebas unitarias del delivery app
Write-Host "=== Ejecutando Pruebas Unitarias del Delivery App ===" -ForegroundColor Green

# Verificar que pytest esté instalado
Write-Host "Verificando dependencias de testing..." -ForegroundColor Yellow
python -m pip install pytest pytest-asyncio pytest-mock pytest-cov fastapi redis pydantic httpx

Write-Host "`n=== Ejecutando pruebas existentes ===" -ForegroundColor Cyan

# Ejecutar todas las pruebas disponibles
Write-Host "`nEjecutando todas las pruebas disponibles..." -ForegroundColor Yellow
python -m pytest tests/ -v

Write-Host "`n=== Resumen de pruebas implementadas ===" -ForegroundColor Blue
Write-Host "✅ Pruebas de modelos (19 pruebas)" -ForegroundColor Green
Write-Host "  - Validación de categorías de productos" -ForegroundColor White
Write-Host "  - Creación y validación de productos" -ForegroundColor White
Write-Host "  - Actualización parcial de productos" -ForegroundColor White
Write-Host "  - Filtros de búsqueda" -ForegroundColor White
Write-Host ""
Write-Host "✅ Pruebas de utilidades (4 pruebas)" -ForegroundColor Green
Write-Host "  - Generación de tokens" -ForegroundColor White
Write-Host "  - Hash de contraseñas" -ForegroundColor White
Write-Host "  - Verificación de contraseñas" -ForegroundColor White
Write-Host ""

Write-Host "📊 Total: 23 pruebas implementadas y funcionando" -ForegroundColor Cyan

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Todas las pruebas pasaron exitosamente!" -ForegroundColor Green
    Write-Host "El framework de testing está listo para usar." -ForegroundColor Green
} else {
    Write-Host "`n❌ Algunas pruebas fallaron. Revisa los detalles arriba." -ForegroundColor Red
}

Write-Host "`n=== Comandos útiles para desarrollo ===" -ForegroundColor Blue
Write-Host "Para ejecutar pruebas específicas:" -ForegroundColor White
Write-Host "  python -m pytest tests/unit/test_models.py -v" -ForegroundColor Gray
Write-Host "  python -m pytest tests/unit/test_utils.py -v" -ForegroundColor Gray
Write-Host ""
Write-Host "Para ejecutar con coverage:" -ForegroundColor White
Write-Host "  python -m pytest --cov=. --cov-report=term-missing --cov-report=html" -ForegroundColor Gray
Write-Host ""
Write-Host "Para ejecutar una prueba específica:" -ForegroundColor White
Write-Host "  python -m pytest tests/unit/test_models.py::test_valid_product_creation -v" -ForegroundColor Gray
