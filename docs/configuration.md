# Configuración

> [← Volver al índice](index.md)

---

## Variables de entorno (`.env`)

Copia `.env.example` a `.env` y completa los valores. Las variables marcadas con ✅ son requeridas para que el sistema funcione.

### LLM — Modelos de lenguaje

| Variable | Requerido | Descripción | Ejemplo |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ (si usas Gemini) | API Key de Google AI Studio | `AIza...` |
| `OPENROUTER_API_KEY` | ❌ | API Key de OpenRouter (alternativa) | `sk-or-...` |
| `NVIDIA_API_KEY` | ❌ | API Key de NVIDIA NIM (fallback automático) | `nvapi-...` |
| `MODEL` | ❌ | Modelo activo | `google/gemini-2.5-pro` |
| `OPENAI_API_BASE` | ❌ | Endpoint base si usas proxy o OpenRouter | `https://openrouter.ai/api/v1` |

**Modelos soportados (ejemplos):**

| Proveedor | Valor de `MODEL` |
|---|---|
| Google Gemini 2.5 Pro | `google/gemini-2.5-pro` |
| Google Gemini Flash | `gemini/gemini-flash-latest` |
| Meta Llama 3.1 (NVIDIA) | `openai/meta/llama-3.1-8b-instruct` |
| OpenRouter + Claude | `openrouter/anthropic/claude-3.5-sonnet` |

> El sistema prueba el modelo principal 3 veces con backoff exponencial.  
> Si falla, hace fallback automático a NVIDIA NIM si `NVIDIA_API_KEY` está configurado.

---

### WordPress — Credenciales

| Variable | Requerido | Descripción |
|---|---|---|
| `WP_URL` | ✅ | URL base del sitio (sin `/` al final) |
| `WP_USERNAME` | ✅ | Nombre de usuario administrador |
| `WP_APP_PASSWORD` | ✅ | Application Password (con espacios, como WordPress lo muestra) |

> **¿Dónde generar una Application Password?**  
> Panel de WordPress → Usuarios → Tu perfil → desplaza hasta "Contraseñas de aplicación" → escribe un nombre → clic en "Agregar nueva contraseña de aplicación".

---

### Identidad del sitio — JSON-LD Schema

Estas variables personalizan el schema `TechArticle` inyectado por `inject_json_ld_schema`.  
Si no se configuran, el sistema usa valores derivados de `WP_URL`.

| Variable | Default | Descripción |
|---|---|---|
| `WP_SITE_NAME` | dominio de `WP_URL` | Nombre del sitio en el schema de publisher |
| `WP_SITE_LOGO` | *(vacío)* | URL absoluta al logo (incluye el campo `logo` en el schema si se provee) |
| `WP_AUTHOR_NAME` | `"WordPress AI Content Agent"` | Nombre del autor en el schema |
| `WP_AUTHOR_URL` | valor de `WP_URL` | URL del perfil del autor |

---

### Imágenes

| Variable | Requerido | Descripción |
|---|---|---|
| `FAL_KEY` | ❌ | API Key de fal.ai para generación de imágenes. Sin ella se usa Pollinations.ai como preview. |

---

### Sistema

| Variable | Default | Descripción |
|---|---|---|
| `PYTHONIOENCODING` | `utf-8` | Encoding para salida en Windows — **no cambiar** |
| `DEBUG` | `false` | Activa logs más verbosos si se pone `true` |

---

## `data/categories.json`

Mapeo de nombres de categoría (en minúsculas) a IDs de WordPress.  
Este archivo evita hardcodear IDs en el código y se puede actualizar sin tocar Python.

### Formato

```json
{
  "_comment": "Este campo se ignora. Añade tus categorías debajo.",
  "nombre-de-categoria": 123,
  "otra-categoria": 456
}
```

### Cómo obtener los IDs de tus categorías

Usa la tool `get_wordpress_categories` desde el cliente MCP:
```
Obtén todas las categorías de https://mi-sitio.com con usuario admin y mi-app-password
```

O directamente con curl:
```bash
curl -u "usuario:app-password" https://tu-sitio.com/wp-json/wp/v2/categories
```

### Comportamiento sin el archivo

Si `data/categories.json` no existe o no puede leerse, el sistema:
1. Registra una advertencia en el log
2. Usa un mapa vacío `{}` como fallback
3. Los nombres de categoría no conocidos se omiten (sin error)

---

## Flujo de selección del modelo LLM

```
¿MODEL definido en .env?
        │
    Sí  ├─── ¿Contiene "gemini" o "google"?
        │              │
        │         Sí   ├── Usa GEMINI_API_KEY
        │         No   └── Usa OPENAI_API_BASE + NVIDIA_API_KEY o OPENAI_API_KEY
        │
    No  └─── Default: openai/meta/llama-3.1-8b-instruct (requiere NVIDIA_API_KEY)

Si el modelo primario falla 3 veces:
    └── ¿NVIDIA_API_KEY disponible y no es ya el modelo primario?
                │
            Sí  └── Fallback a openai/meta/llama-3.1-8b-instruct via NVIDIA NIM
            No  └── Lanza RuntimeError
```

---

## Ejemplo de `.env` completo

```env
# ─── LLM ────────────────────────────────────────────
GEMINI_API_KEY="AIzaSy..."
MODEL="google/gemini-2.5-pro"

# ─── FALLBACK LLM (opcional) ────────────────────────
NVIDIA_API_KEY="nvapi-..."

# ─── IMÁGENES (opcional) ────────────────────────────
FAL_KEY="..."

# ─── WORDPRESS ──────────────────────────────────────
WP_URL="https://mi-blog-tech.com"
WP_USERNAME="mi-admin"
WP_APP_PASSWORD="AbcD eFgH iJkL mNoP qRsT"

# ─── IDENTIDAD DEL SITIO (para JSON-LD) ─────────────
WP_SITE_NAME="Mi Blog Tech"
WP_SITE_LOGO="https://mi-blog-tech.com/wp-content/uploads/logo.png"
WP_AUTHOR_NAME="Equipo Editorial"
WP_AUTHOR_URL="https://mi-blog-tech.com/about"

# ─── SISTEMA ────────────────────────────────────────
PYTHONIOENCODING=utf-8
DEBUG=false
```
