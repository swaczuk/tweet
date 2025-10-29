#!/bin/bash

# Script rápido para probar el sistema sin BigQuery

echo "=========================================="
echo "LOG PROCESSOR - TEST RÁPIDO"
echo "=========================================="
echo ""

# Paso 1: Generar logs de ejemplo
echo "1. Generando logs de ejemplo..."
python generate_sample_logs.py

if [ ! -f "logs_ejemplo.zip" ]; then
    echo "❌ Error: No se pudo generar logs_ejemplo.zip"
    exit 1
fi

echo ""
echo "=========================================="

# Paso 2: Procesar logs (sin subir a BigQuery)
echo "2. Procesando logs..."
echo ""

python process_logs.py logs_ejemplo.zip \
    --month 2024-01-01 \
    --project-id dummy \
    --dataset-id dummy \
    --no-upload \
    --output-json test_results.json

if [ ! -f "test_results.json" ]; then
    echo ""
    echo "❌ Error: No se pudo generar test_results.json"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ TEST COMPLETADO"
echo "=========================================="
echo ""
echo "Archivos generados:"
echo "  - logs_ejemplo.zip (logs de prueba)"
echo "  - test_results.json (resultados del procesamiento)"
echo ""
echo "Para ver los resultados:"
echo "  cat test_results.json | python -m json.tool | less"
echo ""
echo "Para limpiar:"
echo "  rm logs_ejemplo.zip test_results.json"
echo ""
