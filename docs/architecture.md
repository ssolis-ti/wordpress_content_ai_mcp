# Arquitectura del Sistema

> [← Volver al índice](index.md)

---

## Visión general

El sistema sigue una **arquitectura en capas** donde cada capa tiene una única responsabilidad y no conoce los detalles internos de las demás.

```
┌─────────────────────────────────────────────────────┐
│                  CAPA DE INTERFACES                  │
│  bridge/mcp_server.py   portero/agent.py (CLI)       │
│         (MCP stdio)          (experimental)          │
└──────────────────────┬──────────────────────────────┘
                       │ llama a
┌──────────────────────▼──────────────────────────────┐
│                   CAPA DE FACHADA                    │
│                   app/core.py                        │
│              ContentGenerator (Fachada)              │
│           get_content_generator() singleton          │
└────┬─────────┬──────────┬──────────┬────────────────┘
     │         │          │          │
┌────▼──┐ ┌───▼───┐ ┌────▼──┐ ┌────▼──────┐ ┌──────┐
│genera-│ │ seo.  │ │resear-│ │publisher. │ │image.│
│tor.py │ │  py   │ │ch.py  │ │    py     │ │  py  │
│       │ │       │ │       │ │           │ │      │
│Content│ │SEOAud-│ │Topic  │ │WordPress  │ │Image │
│Genera-│ │itor   │ │Resear-│ │Publisher  │ │Gener-│
│torEng.│ │       │ │cher   │ │           │ │ator  │
└───┬───┘ └───┬───┘ └───┬───┘ └─────┬─────┘ └──┬───┘
    │         │          │           │            │
    └─────────┴──────────┴───────────┴────────────┘
                         │ llaman a
┌────────────────────────▼────────────────────────────┐
│                  CAPA DE SERVICIOS                   │
│     app/llm.py          app/storage.py               │
│   call_llm()           JSONStorage[T]                │
│  (LiteLLM + retry)    (persistencia JSON)            │
└─────────────────────────────────────────────────────┘
```

---

## Componentes principales

### `bridge/mcp_server.py` — Capa MCP
**Responsabilidad única:** transporte de mensajes MCP.

- No contiene lógica de negocio
- Define schemas JSON de las 13 tools
- Ruteador `call_tool()` → handlers individuales
- `load_dotenv()` al inicio garantiza que los keys estén disponibles

### `app/core.py` — Fachada
**Responsabilidad única:** una sola interfaz para todos los casos de uso.

```python
class ContentGenerator:
    generator: ContentGeneratorEngine
    auditor:   SEOAuditor
    researcher: TopicResearcher
    publisher: WordPressPublisher

def get_content_generator() -> ContentGenerator:
    # Singleton — una sola instancia por proceso
```

El patrón Singleton garantiza que los engines se instancian una sola vez, ahorrando tiempo de inicialización en cada llamada MCP.

### `app/generator.py` — Motor de Contenido
- Genera artículos Markdown usando el LLM
- Mapea `tone` (string) → `ContentTone` (enum) con fallback a `PROFESSIONAL`
- Genera meta description con LLM (no plantilla)
- Calcula SEO score real delegando a `SEOAuditor`
- Normaliza slugs (incluyendo caracteres acentuados)

### `app/seo.py` — Motor SEO
**Métricas deterministas** (sin LLM):
- `keyword_density`: regex de frecuencia, rango óptimo 1-3%
- `readability`: longitud media de oraciones
- `meta_optimization`: detección de H1/H2/H3 con regex
- `technical_seo`: cobertura de keywords secundarias

**LLM para optimización:**
- `_optimize_content()`: aplica las recomendaciones al texto
- `audit_seo_entities()`: identifica entidades técnicas presentes/faltantes

### `app/research.py` — Motor de Investigación
Todos los métodos usan el LLM con prompts estructurados:
- `_generate_key_findings()` → lista numerada
- `_generate_competitor_analysis()` → JSON estructurado
- `_generate_trends()` → lista numerada
- `_generate_sources()` → lista de URLs relevantes

### `app/publisher.py` — Motor WordPress
- Comunica con la REST API v2 de WordPress
- Convierte Markdown → HTML con la librería `markdown`
- Carga el mapeo de categorías desde `data/categories.json`
- Métodos especializados: `inject_json_ld_schema`, `suggest_internal_links`, `apply_internal_links`

### `app/llm.py` — Cliente LLM
```
call_llm(prompt, max_tokens)
    │
    ├── load_dotenv() (al importar el módulo)
    ├── Detecta proveedor por MODEL env var
    ├── Intento 1 → espera 2s → Intento 2 → espera 4s → Intento 3
    └── Fallback NVIDIA NIM si NVIDIA_API_KEY disponible
```

### `app/models.py` — Modelos de datos
Pydantic v2 con validación completa:

```python
class BlogPost(BaseModel):
    metadata: ContentMetadata
    content: str
    tone: ContentTone          # enum
    seo_score: SEOScore        # 0-100 por dimensión
    seo_recommendations: List[SEORecommendation]

class SEOScore(BaseModel):
    overall: float             # Field(ge=0, le=100)
    readability: float
    keyword_density: float
    meta_optimization: float
    technical_seo: float
```

### `app/storage.py` — Persistencia
```python
class JSONStorage(Generic[T]):
    def save(item: T) -> T
    def get(id: str) -> Optional[T]
    def list() -> List[T]
    def delete(id: str) -> bool
```
Generic sobre cualquier modelo Pydantic. Guarda en `data/{ModelName}.json`.

---

## Flujo de una llamada típica

**Ejemplo: `generate_blog_post`**

```
Cliente MCP
    │
    │ tools/call → generate_blog_post
    ▼
mcp_server.py :: call_tool("generate_blog_post", args)
    │
    ▼
mcp_server.py :: _generate_blog_post(args)
    │
    ▼
core.py :: ContentGenerator.generate_blog_post(topic, keywords, ...)
    │
    ▼
generator.py :: ContentGeneratorEngine.generate_blog_post(...)
    │
    ├── llm.py :: call_llm(prompt_articulo)        → str (Markdown)
    ├── llm.py :: call_llm(prompt_meta_desc)       → str (meta)
    ├── seo.py :: SEOAuditor._calculate_seo_score  → SEOScore
    └── models.py :: BlogPost(...)                 → BlogPost
    │
    ▼
mcp_server.py :: _ok({title, content, seo_score, ...})
    │
    ▼
Cliente MCP recibe JSON
```

---

## Patrones de diseño aplicados

| Patrón | Dónde | Por qué |
|---|---|---|
| **Fachada** | `app/core.py` | Una sola interfaz simplificada para el cliente MCP |
| **Singleton** | `get_content_generator()` | Evita re-instanciar engines en cada llamada |
| **Generic** | `JSONStorage[T]` | Reutiliza lógica CRUD para cualquier modelo Pydantic |
| **Strategy** | `_parse_tone()` en generator | Mapeo configurable de string → enum |
| **Dispatcher** | `call_tool()` en mcp_server | Routing explícito sin condicionales anidados |

---

## Decisiones de diseño

### ¿Por qué `stdio` y no HTTP?
MCP sobre stdio es el estándar para servidores locales. El cliente MCP lanza el proceso Python y se comunica por stdin/stdout. No requiere configurar puertos, firewall, ni autenticación de red.

### ¿Por qué el logging va a `stderr`?
El protocolo MCP usa `stdout` para el protocolo JSON-RPC. Cualquier log en `stdout` rompería el protocolo. `stderr` es el canal correcto para diagnóstico.

### ¿Por qué Pydantic para los modelos?
- Validación automática en runtime (rangos 0-100, enums tipados)
- `.model_dump()` para serialización directa a JSON
- Integración nativa con mypy para análisis estático

### ¿Por qué `categories.json` y no env vars?
Las categorías son muchas y cambian por sitio. Un archivo JSON es más legible, versionable en git, y no infla el `.env`. Se recarga automáticamente al iniciar el proceso.
