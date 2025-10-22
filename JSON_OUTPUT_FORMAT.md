# JSON Output Format

El scraper devuelve los resultados en el siguiente formato JSON estructurado:

## Estructura Completa

```json
{
  "query": "búsqueda realizada",
  "language": "en",
  "region": "US",
  "ai_overview": "Texto del resumen generado por IA de Google (si está disponible)",
  "total_results": 10,
  "results": [
    {
      "url": "https://example.com/page1",
      "title": "Título de la Página 1",
      "meta_description": "Descripción completa o snippet que muestra Google para este resultado",
      "highlighted_text": "texto destacado | más texto destacado | otro texto destacado"
    },
    {
      "url": "https://example.com/page2",
      "title": "Título de la Página 2",
      "meta_description": "Otra descripción del resultado",
      "highlighted_text": "palabras que Google enfatizó"
    }
  ]
}
```

## Campos Principales

### Nivel Superior

- **query** (string): La consulta de búsqueda realizada
- **language** (string): Código de idioma (ej: "en", "es", "fr")
- **region** (string): Código de región (ej: "US", "ES", "MX")
- **ai_overview** (string|null): Resumen generado por Google AI Mode (puede ser null si no está disponible)
- **total_results** (number): Número total de resultados encontrados
- **results** (array): Lista de resultados de búsqueda

### Cada Resultado en el Array "results"

Cada resultado está **completamente separado** y contiene:

- **url** (string): URL completa de la página web
- **title** (string): Título de la página según Google
- **meta_description** (string): Descripción o snippet completo que Google muestra
- **highlighted_text** (string|null):
  - Texto que Google **destacó/enfatizó** en negritas o énfasis
  - Múltiples fragmentos destacados se separan con " | "
  - Puede ser null si no hay texto destacado

## Ejemplo Real

```json
{
  "query": "what is artificial intelligence",
  "language": "en",
  "region": "US",
  "ai_overview": "Artificial intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction...",
  "total_results": 8,
  "results": [
    {
      "url": "https://www.ibm.com/topics/artificial-intelligence",
      "title": "What is Artificial Intelligence (AI)? | IBM",
      "meta_description": "Artificial intelligence leverages computers and machines to mimic the problem-solving and decision-making capabilities of the human mind. AI enables technical systems to perceive their environment, deal with what they perceive and solve problems.",
      "highlighted_text": "problem-solving | decision-making capabilities | human mind"
    },
    {
      "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
      "title": "Artificial intelligence - Wikipedia",
      "meta_description": "Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of intelligent agents.",
      "highlighted_text": "intelligence demonstrated by machines | intelligent agents"
    },
    {
      "url": "https://www.britannica.com/technology/artificial-intelligence",
      "title": "Artificial intelligence (AI) | Definition, Examples ... - Britannica",
      "meta_description": "Artificial intelligence is the ability of a computer or computer-controlled robot to perform tasks that are commonly associated with intelligent beings.",
      "highlighted_text": "perform tasks | intelligent beings"
    }
  ]
}
```

## Características Importantes

### ✅ Separación por URL

Cada URL tiene sus propios datos asociados:
- Su propio título
- Su propia descripción
- Su propio texto destacado

### ✅ Texto Destacado por Resultado

El campo `highlighted_text` contiene **solo** el texto que Google destacó para **ese resultado específico**.

Si Google destacó múltiples fragmentos en un mismo resultado, se concatenan con ` | `:
```json
"highlighted_text": "primer fragmento destacado | segundo fragmento | tercer fragmento"
```

### ✅ Valores Nulos

- `ai_overview` puede ser `null` si Google AI Mode no genera resumen
- `highlighted_text` puede ser `null` si Google no destacó ningún texto para ese resultado específico

## Uso Programático

### Python

```python
from google_ai_scraper import GoogleAIModeScraper
import json

with GoogleAIModeScraper(headless=True) as scraper:
    result = scraper.scrape("your query", language="en", region="US")

    # Acceder a resultados individuales
    for res in result.results:
        print(f"URL: {res.url}")
        print(f"Title: {res.title}")
        print(f"Description: {res.meta_description}")
        print(f"Highlights: {res.ai_highlight}")
        print("-" * 60)

    # Convertir a JSON
    from dataclasses import asdict
    json_data = asdict(result)

    # Guardar
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
```

### JavaScript

```javascript
// Leer el JSON
const data = JSON.parse(fs.readFileSync('results.json', 'utf8'));

// Iterar sobre resultados
data.results.forEach(result => {
  console.log(`URL: ${result.url}`);
  console.log(`Title: ${result.title}`);
  console.log(`Description: ${result.meta_description}`);
  console.log(`Highlights: ${result.highlighted_text}`);
  console.log('-'.repeat(60));
});
```

## Garantías

El formato JSON garantiza que:

1. ✅ Cada URL tiene su información completa y separada
2. ✅ El texto destacado pertenece únicamente a su resultado correspondiente
3. ✅ La estructura es consistente y predecible
4. ✅ Los datos están codificados en UTF-8 para soportar múltiples idiomas
5. ✅ Los resultados mantienen el orden en que aparecen en Google
