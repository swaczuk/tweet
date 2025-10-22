# Nuevo Formato JSON - Estructura Mejorada

El scraper ahora devuelve los resultados en un formato JSON **más claro y estructurado** donde cada URL está perfectamente separada.

## 📋 Estructura JSON

```json
{
  "search_info": {
    "query": "consulta de búsqueda",
    "language": "en",
    "region": "US",
    "total_results": 10
  },
  "ai_overview": "Resumen generado por Google AI Mode...",
  "urls": [
    {
      "position": 1,
      "url": "https://example.com/page1",
      "title": "Título de la Página 1",
      "meta_description": "Descripción completa que muestra Google",
      "highlighted_text": "texto destacado | más texto | otro texto"
    },
    {
      "position": 2,
      "url": "https://example.com/page2",
      "title": "Título de la Página 2",
      "meta_description": "Otra descripción",
      "highlighted_text": "palabras enfatizadas"
    }
  ]
}
```

## 🎯 Ventajas del Nuevo Formato

### ✅ Información de Búsqueda Agrupada

Todo lo relacionado con la búsqueda está en `search_info`:
- Query original
- Idioma
- Región
- Total de resultados

### ✅ URLs Completamente Separadas

Cada elemento en el array `urls` representa **una URL única** con:
- `position`: Posición en los resultados (1, 2, 3...)
- `url`: URL completa de la página
- `title`: Título de la página
- `meta_description`: Descripción/snippet completo
- `highlighted_text`: Texto que Google destacó para **esta URL específica**

### ✅ Sin Valores Null

- Los campos vacíos se devuelven como string vacío `""` en lugar de `null`
- Más fácil de manejar en JavaScript/Python
- Evita errores por valores nulos

## 📖 Ejemplo Real Completo

```json
{
  "search_info": {
    "query": "what is artificial intelligence",
    "language": "en",
    "region": "US",
    "total_results": 8
  },
  "ai_overview": "Artificial intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction. Specific applications of AI include expert systems, natural language processing, speech recognition and machine vision.",
  "urls": [
    {
      "position": 1,
      "url": "https://www.ibm.com/topics/artificial-intelligence",
      "title": "What is Artificial Intelligence (AI)? | IBM",
      "meta_description": "Artificial intelligence leverages computers and machines to mimic the problem-solving and decision-making capabilities of the human mind.",
      "highlighted_text": "problem-solving | decision-making capabilities | human mind"
    },
    {
      "position": 2,
      "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
      "title": "Artificial intelligence - Wikipedia",
      "meta_description": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals.",
      "highlighted_text": "intelligence demonstrated by machines | intelligent agents"
    },
    {
      "position": 3,
      "url": "https://www.britannica.com/technology/artificial-intelligence",
      "title": "Artificial intelligence (AI) | Definition ... - Britannica",
      "meta_description": "Artificial intelligence is the ability of a computer or computer-controlled robot to perform tasks that are commonly associated with intelligent beings.",
      "highlighted_text": "perform tasks | intelligent beings"
    }
  ]
}
```

## 💻 Uso Programático

### Python

```python
import requests
import json

# Llamar a la API
response = requests.post('http://localhost:5000/api/scrape', json={
    'query': 'artificial intelligence',
    'language': 'en',
    'region': 'US'
})

data = response.json()

# Acceder a la información
print(f"Búsqueda: {data['search_info']['query']}")
print(f"Total resultados: {data['search_info']['total_results']}")

if data['ai_overview']:
    print(f"\nAI Overview:\n{data['ai_overview']}")

# Iterar sobre las URLs
for url_data in data['urls']:
    print(f"\n#{url_data['position']} - {url_data['title']}")
    print(f"URL: {url_data['url']}")
    print(f"Descripción: {url_data['meta_description']}")
    if url_data['highlighted_text']:
        print(f"Destacado: {url_data['highlighted_text']}")
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:5000/api/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'artificial intelligence',
    language: 'en',
    region: 'US'
  })
});

const data = await response.json();

// Acceder a la información
console.log(`Búsqueda: ${data.search_info.query}`);
console.log(`Total: ${data.search_info.total_results} resultados`);

if (data.ai_overview) {
  console.log(`\nAI Overview:\n${data.ai_overview}`);
}

// Iterar sobre las URLs
data.urls.forEach(url_data => {
  console.log(`\n#${url_data.position} - ${url_data.title}`);
  console.log(`URL: ${url_data.url}`);
  console.log(`Descripción: ${url_data.meta_description}`);
  if (url_data.highlighted_text) {
    console.log(`Destacado: ${url_data.highlighted_text}`);
  }
});
```

### PHP

```php
<?php
$response = file_get_contents('http://localhost:5000/api/scrape', false, stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => 'Content-Type: application/json',
        'content' => json_encode([
            'query' => 'artificial intelligence',
            'language' => 'en',
            'region' => 'US'
        ])
    ]
]));

$data = json_decode($response, true);

echo "Búsqueda: " . $data['search_info']['query'] . "\n";
echo "Total: " . $data['search_info']['total_results'] . " resultados\n";

if (!empty($data['ai_overview'])) {
    echo "\nAI Overview:\n" . $data['ai_overview'] . "\n";
}

foreach ($data['urls'] as $url_data) {
    echo "\n#" . $url_data['position'] . " - " . $url_data['title'] . "\n";
    echo "URL: " . $url_data['url'] . "\n";
    echo "Descripción: " . $url_data['meta_description'] . "\n";
    if (!empty($url_data['highlighted_text'])) {
        echo "Destacado: " . $url_data['highlighted_text'] . "\n";
    }
}
?>
```

## 🔧 API Endpoints

### POST /api/scrape

Escanea una sola búsqueda.

**Request:**
```json
{
  "query": "your search query",
  "language": "en",
  "region": "US"
}
```

**Response:** Objeto JSON con la estructura descrita arriba.

### POST /api/scrape/batch

Escanea múltiples búsquedas.

**Request:**
```json
{
  "queries": ["query1", "query2", "query3"],
  "language": "en",
  "region": "US"
}
```

**Response:** Array de objetos JSON, cada uno con la estructura descrita.

## 📊 Características Clave

1. **Legibilidad**: Estructura clara y fácil de entender
2. **Consistencia**: Todos los campos siempre presentes (nunca undefined)
3. **Separación**: Cada URL está completamente aislada con su información
4. **Position**: Número de posición para mantener el orden de Google
5. **UTF-8**: Soporte completo para múltiples idiomas

## 🌐 Interfaz Web

La interfaz web en `http://localhost:5000` consume esta API automáticamente y muestra los resultados de forma visual y organizada.

Características:
- Formulario para ingresar búsqueda, idioma y región
- Vista previa de AI Overview
- Resultados mostrados en tarjetas separadas por URL
- Botón para exportar JSON
- Diseño responsive
