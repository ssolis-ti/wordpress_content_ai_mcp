# WordPress AI Content System — Documentación

> Sistema de generación, auditoría SEO y publicación de contenido para WordPress,  
> impulsado por LLM y expuesto como servidor MCP.

---

## 📚 Índice de Documentación

| Documento | Descripción |
|---|---|
| [📖 Guía de Inicio Rápido](getting-started.md) | Instalación, configuración del `.env` y primera conexión MCP |
| [🔧 Referencia de Herramientas MCP](mcp-tools.md) | Las 13 tools: parámetros, respuestas y ejemplos de uso |
| [⚙️ Configuración](configuration.md) | Variables de entorno, `categories.json`, modelos LLM |
| [🏗️ Arquitectura](architecture.md) | Capas del sistema, patrones de diseño, diagrama de flujo |
| [🧪 Verificación y QA](verification-qa.md) | Pruebas unitarias offline, auditoría de código y robustez |
| [🛡️ Identidad del Agente (Portero)](PORTERO.md) | Identidad, directrices y ejemplos del agente inteligente |

---

## ¿Qué es este sistema?

Un servidor **MCP (Model Context Protocol)** escrito en Python que expone capacidades de creación y publicación de contenido WordPress a cualquier cliente IA compatible:

- [opencode](https://opencode.ai)
- [openclaw](https://openclaw.ai)
- [Claude Desktop](https://claude.ai/desktop)
- [Cursor](https://cursor.sh)

### Capacidades principales

```
Investigar temas  →  Generar artículos  →  Auditar SEO  →  Publicar en WordPress
       ↓                    ↓                   ↓                    ↓
 research_topic    generate_blog_post   seo_audit_and_    publish_to_wordpress
                                          optimize
```

### Stack tecnológico

| Componente | Tecnología |
|---|---|
| Protocolo | MCP 1.0+ (stdio) |
| Lenguaje | Python 3.10+ |
| LLM | LiteLLM (Gemini, OpenRouter, NVIDIA NIM) |
| Validación | Pydantic v2 |
| WordPress | REST API v2 |
| Imágenes | fal.ai (flux/schnell) |
| Persistencia | JSON local |

---

## Inicio rápido en 3 pasos

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar credenciales
cp .env.example .env
# Editar .env con tu GEMINI_API_KEY, WP_URL, etc.

# 3. Conectar al cliente MCP
# Añadir a la config de opencode/openclaw/Claude Desktop:
# { "command": "python", "args": ["bridge/mcp_server.py"] }
```

---

## Estructura del proyecto

```
wp_mcp_content_ai/
├── bridge/
│   └── mcp_server.py          # Servidor MCP (punto de entrada)
├── app/
│   ├── core.py                # Fachada principal
│   ├── generator.py           # Motor de generación de contenido
│   ├── seo.py                 # Motor de auditoría SEO
│   ├── research.py            # Motor de investigación de temas
│   ├── publisher.py           # Motor de publicación WordPress
│   ├── image.py               # Motor de generación de imágenes
│   ├── llm.py                 # Cliente LLM resiliente
│   ├── models.py              # Modelos de datos (Pydantic)
│   └── storage.py             # Persistencia JSON
├── portero/
│   ├── agent.py               # Agente CLI (experimental)
│   └── tools.py               # Wrappers de herramientas
├── data/
│   └── categories.json        # Mapeo de categorías WordPress
├── docs/
│   ├── index.md               # Este archivo
│   ├── getting-started.md     # Guía de inicio
│   ├── mcp-tools.md           # Referencia de tools
│   ├── configuration.md       # Configuración detallada
│   └── architecture.md        # Arquitectura del sistema
├── tests/
│   └── test_core.py
├── .env.example
└── requirements.txt
```
