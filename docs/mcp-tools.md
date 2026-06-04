# Referencia de Herramientas MCP

> [← Volver al índice](index.md)

El servidor expone **13 herramientas** agrupadas en 4 categorías.

---

## Índice de Tools

| # | Tool | Categoría | Descripción breve |
|---|---|---|---|
| 1 | [`generate_blog_post`](#1-generate_blog_post) | Contenido | Genera un artículo SEO completo |
| 2 | [`seo_audit_and_optimize`](#2-seo_audit_and_optimize) | SEO | Audita y optimiza contenido existente |
| 3 | [`audit_seo_entities`](#3-audit_seo_entities) | SEO | Auditoría semántica de entidades técnicas |
| 4 | [`research_topic`](#4-research_topic) | Investigación | Investiga un tema con LLM |
| 5 | [`publish_to_wordpress`](#5-publish_to_wordpress) | WordPress | Publica un BlogPost generado |
| 6 | [`create_wordpress_post`](#6-create_wordpress_post) | WordPress | Crea un post desde Markdown directo |
| 7 | [`get_wordpress_posts`](#7-get_wordpress_posts) | WordPress | Lista posts existentes |
| 8 | [`get_wordpress_categories`](#8-get_wordpress_categories) | WordPress | Lista categorías del sitio |
| 9 | [`update_wordpress_post`](#9-update_wordpress_post) | WordPress | Actualiza un post existente |
| 10 | [`inject_json_ld_schema`](#10-inject_json_ld_schema) | SEO Técnico | Inyecta JSON-LD TechArticle |
| 11 | [`suggest_internal_links`](#11-suggest_internal_links) | SEO Técnico | Sugiere enlaces internos contextuales |
| 12 | [`apply_internal_links`](#12-apply_internal_links) | SEO Técnico | Aplica enlaces internos automáticamente |
| 13 | [`generate_image_asset`](#13-generate_image_asset) | Imágenes | Genera imágenes con fal.ai |

---

## Categoría: Contenido

### 1. `generate_blog_post`

Genera un artículo completo en Markdown, optimizado para SEO, a partir de un tema y palabras clave.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `topic` | string | ✅ | — | Tema principal del artículo |
| `target_keywords` | list[string] | ❌ | [topic] | Keywords SEO a incluir |
| `word_count` | integer | ❌ | 1200 | Extensión objetivo (100–10000) |
| `tone` | string | ❌ | "professional" | Tono de escritura (ver valores válidos) |
| `target_audience` | string | ❌ | "general" | Audiencia objetivo |

**Valores válidos para `tone`:**
`professional` · `casual` · `authoritative` · `conversational` · `technical` · `persuasive`

**Respuesta:**
```json
{
  "success": true,
  "title": "Título del artículo",
  "content": "# Título\n\n## Sección 1\n\n...",
  "meta_description": "Descripción SEO de 140-160 caracteres",
  "slug": "titulo-del-articulo",
  "word_count": 1200,
  "reading_time_minutes": 6,
  "tone": "professional",
  "target_audience": "developers",
  "target_keywords": ["blockchain", "supply chain"],
  "categories": ["Noticias"],
  "tags": ["blockchain", "supply chain"],
  "images_suggestions": ["Futuristic image representing blockchain and supply chain"],
  "seo_score": {
    "overall": 78.5,
    "readability": 82.0,
    "keyword_density": 71.0,
    "meta_optimization": 80.0,
    "technical_seo": 75.0
  }
}
```

**Ejemplo de uso:**
```
Genera un artículo de 1500 palabras sobre "zero-knowledge proofs en finanzas DeFi",
tono técnico, para una audiencia de desarrolladores blockchain.
Keywords: ZK proofs, privacidad, Ethereum, rollups.
```

---

## Categoría: SEO

### 2. `seo_audit_and_optimize`

Audita contenido Markdown existente con métricas reales y devuelve una versión optimizada.

**Métricas calculadas:**
- **Keyword Density** (30%): Densidad ideal 1-3%, penalización por stuffing
- **Readability** (25%): Longitud media de oraciones (ideal: 15-20 palabras)
- **Meta Optimization** (25%): Presencia y calidad de H1, H2, H3
- **Technical SEO** (20%): Cobertura de keywords secundarias

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `content` | string | ✅ | Texto en Markdown a analizar |
| `primary_keyword` | string | ✅ | Keyword principal |
| `secondary_keywords` | list[string] | ❌ | Keywords secundarias a verificar |

**Respuesta:**
```json
{
  "success": true,
  "seo_score": {
    "overall": 83.2,
    "readability": 88.0,
    "keyword_density": 76.5,
    "meta_optimization": 90.0,
    "technical_seo": 75.0
  },
  "recommendations": [
    {
      "category": "Keyword Density",
      "issue": "La keyword 'blockchain' tiene baja densidad (score: 45/100).",
      "suggestion": "Incluye 'blockchain' en los primeros 100 palabras...",
      "priority": "high"
    }
  ],
  "optimized_content": "# Título optimizado\n\n...",
  "improvements_summary": "Optimization applied: 2 high-priority recommendations addressed.",
  "total_recommendations": 3
}
```

---

### 3. `audit_seo_entities`

Auditoría semántica avanzada: detecta entidades técnicas presentes y faltantes en el contenido.

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `content` | string | ✅ | Texto completo del artículo |
| `topic` | string | ✅ | Tema del artículo |

**Respuesta:**
```json
{
  "present_entities": ["Prueba de Trabajo", "Consenso", "Nodo validador"],
  "missing_entities": ["Prueba de Contribución", "Consenso Determinista", "Slashing"],
  "recommendations": [
    "Integra 'Prueba de Contribución' en la sección de mecanismos de consenso.",
    "Explica el concepto de 'Slashing' en el contexto de penalizaciones de red."
  ]
}
```

---

## Categoría: Investigación

### 4. `research_topic`

Investiga un tema usando el LLM: hallazgos clave, tendencias, análisis competitivo y fuentes.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `topic` | string | ✅ | — | Tema a investigar |
| `depth` | string | ❌ | "basic" | `"basic"` (5 hallazgos, 3 tendencias) o `"comprehensive"` (8 hallazgos, 5 tendencias) |

**Respuesta:**
```json
{
  "success": true,
  "topic": "inteligencia artificial en educación",
  "depth": "comprehensive",
  "key_findings": [
    "El 60% de las instituciones K-12 planean adoptar IA para 2026.",
    "..."
  ],
  "trends": [
    "Personalización del aprendizaje con modelos de lenguaje locales.",
    "..."
  ],
  "competitor_analysis": [
    {
      "competitor": "Khan Academy",
      "strength": "Alta autoridad y contenido gratuito",
      "weakness": "Baja cobertura de temas universitarios avanzados"
    }
  ],
  "sources": [
    "https://edtechmagazine.com",
    "https://arxiv.org",
    "..."
  ],
  "recommendations": [
    "Crea una guía sobre 'cómo implementar tutores IA en aulas presenciales'.",
    "..."
  ]
}
```

---

## Categoría: WordPress

### 5. `publish_to_wordpress`

Publica el objeto BlogPost devuelto por `generate_blog_post` en WordPress.

> ⚠️ **Usa siempre `status: "draft"` primero** para revisar antes de publicar.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `content` | object | ✅ | — | Dict completo devuelto por `generate_blog_post` |
| `wp_url` | string | ✅ | — | URL del sitio WordPress |
| `username` | string | ✅ | — | Usuario administrador |
| `app_password` | string | ✅ | — | Application Password de WordPress |
| `status` | string | ❌ | "draft" | `"draft"` o `"publish"` |
| `categories` | list[string] | ❌ | — | Nombres de categoría (se resuelven desde `categories.json`) |
| `tags` | list[string] | ❌ | — | Tags a aplicar |

**Respuesta:**
```json
{
  "success": true,
  "post_id": 4521,
  "post_url": "https://tu-sitio.com/?p=4521",
  "published_at": "2025-10-15T14:30:00",
  "status": "draft"
}
```

---

### 6. `create_wordpress_post`

Crea un post directamente desde un título y texto Markdown, sin necesitar el objeto BlogPost completo.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `title` | string | ✅ | — | Título del post |
| `content` | string | ✅ | — | Cuerpo en Markdown |
| `wp_url` | string | ✅ | — | URL del sitio |
| `username` | string | ✅ | — | Usuario admin |
| `app_password` | string | ✅ | — | Application Password |
| `status` | string | ❌ | "draft" | `"draft"` o `"publish"` |
| `categories` | list[string] | ❌ | — | Categorías |
| `tags` | list[string] | ❌ | — | Tags |

---

### 7. `get_wordpress_posts`

Recupera una lista paginada de posts del sitio.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `wp_url` | string | ✅ | — | URL del sitio |
| `username` | string | ✅ | — | Usuario admin |
| `app_password` | string | ✅ | — | Application Password |
| `per_page` | integer | ❌ | 10 | Posts por página (máx 100) |
| `page` | integer | ❌ | 1 | Página actual |

**Respuesta:**
```json
{
  "success": true,
  "posts": [
    {"id": 4521, "title": {"rendered": "Título"}, "link": "https://...", "status": "publish", "date": "2025-10-15T14:30:00"}
  ],
  "total": 87,
  "total_pages": 9,
  "current_page": 1
}
```

---

### 8. `get_wordpress_categories`

Lista todas las categorías del sitio con sus IDs para actualizar `categories.json`.

**Parámetros:** `wp_url`, `username`, `app_password` (todos requeridos)

---

### 9. `update_wordpress_post`

Actualiza un post existente por ID. Solo envía los campos que quieres cambiar.

**Parámetros:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `post_id` | integer | ✅ | ID del post en WordPress |
| `wp_url` | string | ✅ | URL del sitio |
| `username` | string | ✅ | Usuario admin |
| `app_password` | string | ✅ | Application Password |
| `title` | string | ❌ | Nuevo título |
| `content` | string | ❌ | Nuevo contenido Markdown |
| `status` | string | ❌ | Nuevo estado del post |
| `slug` | string | ❌ | Nuevo slug URL |
| `categories` | list[string] | ❌ | Nuevas categorías |

---

## Categoría: SEO Técnico

### 10. `inject_json_ld_schema`

Inyecta datos estructurados JSON-LD tipo `TechArticle` en un post existente de WordPress.

> El schema se genera dinámicamente leyendo `WP_SITE_NAME`, `WP_SITE_LOGO`, `WP_AUTHOR_NAME` del `.env`.

**Parámetros:** `post_id`, `wp_url`, `username`, `app_password` (todos requeridos)

**Respuesta:**
```json
{
  "success": true,
  "post_id": 4521,
  "schema": {
    "@context": "https://schema.org",
    "@type": "TechArticle",
    "headline": "Título del artículo",
    "publisher": {"@type": "Organization", "name": "Mi Sitio"},
    "datePublished": "2025-10-15T14:30:00"
  }
}
```

---

### 11. `suggest_internal_links`

Analiza un post y sugiere oportunidades de enlace interno basándose en posts publicados.

**Parámetros:** `post_id`, `wp_url`, `username`, `app_password` (todos requeridos)

**Respuesta:**
```json
{
  "success": true,
  "suggestions": [
    {
      "anchor_text": "prueba de trabajo",
      "target_url": "https://tu-sitio.com/que-es-proof-of-work/",
      "justification": "El anchor existe en el cuerpo del artículo y enlaza naturalmente al concepto explicado en el post referenciado."
    }
  ]
}
```

---

### 12. `apply_internal_links`

Llama internamente a `suggest_internal_links` y luego aplica los enlaces al HTML del post en WordPress.

> Solo reemplaza la **primera ocurrencia** de cada anchor text y omite texto ya enlazado.

**Parámetros:** `post_id`, `wp_url`, `username`, `app_password` (todos requeridos)

**Respuesta:**
```json
{
  "success": true,
  "post_id": 4521,
  "applied": [
    {"anchor_text": "prueba de trabajo", "target_url": "https://..."}
  ]
}
```

---

## Categoría: Imágenes

### 13. `generate_image_asset`

Genera una imagen de alta calidad con fal.ai (modelo flux/schnell).

> Si `FAL_KEY` no está configurado, devuelve una URL de preview de Pollinations.ai.

**Parámetros:**

| Parámetro | Tipo | Requerido | Default | Descripción |
|---|---|---|---|---|
| `prompt` | string | ✅ | — | Descripción de la imagen |
| `image_size` | string | ❌ | "landscape_4_3" | Dimensiones de salida |

**Valores válidos para `image_size`:**
`landscape_4_3` · `landscape_16_9` · `portrait_4_3` · `portrait_16_9` · `square`

**Respuesta:**
```json
{
  "success": true,
  "url": "https://fal.run/.../imagen.webp",
  "prompt": "prompt original",
  "revised_prompt": "prompt enriquecido con modificadores visuales",
  "width": 1280,
  "height": 960,
  "created_at": "2025-10-15T14:30:00"
}
```
