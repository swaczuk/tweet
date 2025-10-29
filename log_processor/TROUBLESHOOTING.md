# Troubleshooting - Diagnóstico de Problemas

## 🔍 Problema: Los números no coinciden con otra herramienta

Si encuentras que los resultados no coinciden con otra herramienta de análisis (ej: 42 eventos vs 400 eventos), usa estos pasos para diagnosticar:

### **Paso 1: Analizar el archivo con debug_parser.py**

Este script te muestra exactamente qué líneas se están parseando y cuáles no:

```bash
cd log_processor
python debug_parser.py tu_archivo_log.txt
```

**Qué buscar:**
- ✅ **Líneas parseadas**: Debería ser >95% del total
- ❌ **Líneas NO parseadas**: Si es >5%, hay un problema con el regex
- 🤖 **Bots detectados**: Debería ser un % razonable de las líneas parseadas

**Ejemplo de salida:**
```
📊 ESTADÍSTICAS:
  Total de líneas:          10,000
  Líneas parseadas:         9,850 (98.5%)
    └─ Bots detectados:     2,340 (23.4%)
    └─ No bots (ignoradas): 7,510 (75.1%)
  ❌ Líneas NO parseadas:   150 (1.5%)
```

Si ves muchas líneas NO parseadas, revisa los ejemplos que muestra el script para ver qué está mal.

### **Paso 2: Comparar resultados detallados**

Usa `compare_results.py` para ver un desglose completo por bot y región:

```bash
python compare_results.py tu_archivo_log.txt
```

**Qué buscar:**
- 📍 Hits por región específica (ej: UK)
- 🤖 Hits por bot específico (ej: ChatGPT)
- 🔍 Combinaciones específicas (ej: ChatGPT en UK)

**Ejemplo de salida:**
```
🌍 REGIÓN: AJG-UK
Total de hits en región: 1,234

  🤖 ChatGPT:
     Total de hits: 456
     URLs únicas: 234
     Top 5 URLs:
       1. [123] https://www.ajg.com/uk/insurance/...
       2. [89]  https://www.ajg.com/uk/business/...
```

### **Paso 3: Verificar User Agents**

El mismo script `compare_results.py` también muestra todos los User Agents únicos:

```bash
python compare_results.py tu_archivo_log.txt | grep -A 30 "USER AGENTS"
```

**Qué buscar:**
- 🤖 Variaciones de User Agents que NO se están detectando
- Bots que no están en nuestra lista

Si encuentras un User Agent de bot que no se detecta, agrégalo al `log_parser.py`.

## 🐛 Problemas Comunes

### Problema 1: Muy pocas líneas parseadas (<90%)

**Causa**: El regex no coincide con el formato de tu log.

**Solución**:
1. Ejecuta `debug_parser.py` y revisa los ejemplos de líneas fallidas
2. Compara con las líneas exitosas
3. Identifica las diferencias (espacios extra, formato diferente, etc.)
4. Ajusta el regex en `log_parser.py`

**Ejemplo de variaciones comunes:**
```python
# Formato estándar
r'(?P<ip>[\d\.]+) - - (?P<timestamp>\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2} (?:AM|PM)) ...'

# Si hay espacios variables
r'(?P<ip>[\d\.]+)\s+-\s+-\s+(?P<timestamp>\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s+(?:AM|PM))\s+...'

# Si la hora puede ser de 1 dígito
r'(?P<timestamp>\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM))'
```

### Problema 2: Bot no detectado

**Causa**: El User Agent del bot no está en `BOT_PATTERNS`.

**Solución**:
1. Ejecuta `compare_results.py` para ver todos los User Agents
2. Identifica el User Agent del bot que falta
3. Agrégalo a `log_parser.py` o usa `--custom-bots`:

```json
// custom_bots.json
{
  "MiBotNuevo": "MiBotNuevo\\/\\d+\\.\\d+"
}
```

```bash
python process_logs.py logs.zip --custom-bots custom_bots.json ...
```

### Problema 3: Región no identificada

**Causa**: La URL no coincide con ningún patrón en `REGION_PATTERNS`.

**Solución**:
1. Ejecuta `compare_results.py` y busca entradas con región "UNKNOWN"
2. Revisa las URLs que no se identifican
3. Agrega el patrón faltante a `log_parser.py`:

```python
REGION_PATTERNS = {
    'MI-REGION': r'midominio\.com/mi-region/',
    # ...
}
```

### Problema 4: Números muy diferentes entre herramientas

**Posibles causas:**

1. **Diferentes definiciones de "bot"**
   - Nuestra herramienta: Solo detecta bots específicos en la lista
   - Otra herramienta: Puede incluir más o menos bots

2. **Diferentes períodos de tiempo**
   - Verifica que estás comparando el mismo período
   - Revisa las fechas en los logs con `compare_results.py`

3. **Diferentes regiones**
   - Verifica que ambas herramientas usan la misma definición de "UK"
   - Nuestra herramienta: `ajg.com/uk/` y `gallagherbassett.com/uk/`

4. **Líneas duplicadas o faltantes**
   - Usa `debug_parser.py` para ver el total de líneas
   - Compara con `wc -l tu_archivo.txt`

5. **Status codes diferentes**
   - Por defecto parseamos todos los status (200, 404, 500, etc.)
   - Otra herramienta puede filtrar por status = 200

## 🔧 Comandos Útiles para Diagnóstico

### Ver total de líneas en un archivo
```bash
wc -l tu_archivo_log.txt
```

### Buscar líneas de ChatGPT manualmente
```bash
grep -i "gpt\|chatgpt" tu_archivo_log.txt | wc -l
```

### Buscar líneas de UK manualmente
```bash
grep "ajg.com/uk/" tu_archivo_log.txt | wc -l
```

### Buscar ChatGPT en UK manualmente
```bash
grep "ajg.com/uk/" tu_archivo_log.txt | grep -i "gpt\|chatgpt" | wc -l
```

### Ver ejemplos de líneas de ChatGPT
```bash
grep -i "gpt\|chatgpt" tu_archivo_log.txt | head -5
```

### Contar User Agents únicos
```bash
grep -oP '"[^"]*"[^"]*$' tu_archivo_log.txt | sort | uniq -c | sort -rn | head -20
```

## 📊 Proceso de Validación Recomendado

1. **Extrae un archivo .txt del ZIP** para pruebas rápidas

2. **Cuenta líneas totales**:
   ```bash
   wc -l archivo.txt
   ```

3. **Ejecuta debug_parser.py**:
   ```bash
   python debug_parser.py archivo.txt
   ```
   - Verifica que >95% de líneas se parseen

4. **Ejecuta compare_results.py**:
   ```bash
   python compare_results.py archivo.txt
   ```
   - Anota los números por bot y región

5. **Compara manualmente con grep**:
   ```bash
   # Contar ChatGPT manualmente
   grep -i "gpt\|chatgpt" archivo.txt | wc -l

   # Debería coincidir con el número en compare_results.py
   ```

6. **Si los números NO coinciden**:
   - Revisa ejemplos de User Agents con `compare_results.py`
   - Busca variaciones del bot que no estamos detectando
   - Ajusta `BOT_PATTERNS` o usa `--custom-bots`

7. **Compara con tu otra herramienta**:
   - Usa los números de `compare_results.py`
   - Verifica que ambas herramientas usen las mismas definiciones

## 📝 Reportar un Problema

Si encuentras un problema que no puedes resolver:

1. Ejecuta los scripts de debugging
2. Guarda las salidas:
   ```bash
   python debug_parser.py archivo.txt > debug_output.txt
   python compare_results.py archivo.txt > compare_output.txt
   ```
3. Incluye ejemplos de líneas problemáticas (sin datos sensibles)
4. Describe qué números esperas vs qué números obtienes

## 🚀 Tips para Optimización

### Para archivos muy grandes (>100MB)

1. **Prueba con una muestra primero**:
   ```bash
   head -10000 archivo_grande.txt > muestra.txt
   python debug_parser.py muestra.txt
   ```

2. **Procesa por partes** si hay problemas de memoria

3. **Usa el modo verbose** para ver progreso:
   ```bash
   python process_logs.py logs.zip ... 2>&1 | tee proceso.log
   ```

### Para múltiples archivos

```bash
# Debugging de todos los .txt en un directorio
for file in *.txt; do
    echo "Procesando $file..."
    python debug_parser.py "$file" > "debug_$file.txt"
done
```
