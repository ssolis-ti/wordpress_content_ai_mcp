# Guía de Inicio Rápido

> [← Volver al índice](index.md)

---

## Requisitos previos

| Requisito | Versión mínima |
|---|---|
| Python | 3.10+ |
| pip | cualquier versión reciente |
| WordPress | 5.0+ con REST API habilitada |
| Cliente MCP | opencode / openclaw / Claude Desktop / Cursor |

---

## 1. Instalación

```bash
# Clonar o descargar el proyecto
cd wp_mcp_content_ai

# Instalar dependencias
pip install -r requirements.txt
```

**Dependencias instaladas:**
- `mcp` — protocolo MCP oficial
- `litellm` — cliente LLM multi-proveedor
- `pydantic` — validación de datos
- `requests` — llamadas a la REST API de WordPress
- `fal-client` — generación de imágenes
- `python-dotenv` — carga de variables de entorno
- `markdown` — conversión Markdown → HTML para WordPress

---

## 2. Configuración del entorno

```bash
# Copiar la plantilla
cp .env.example .env
```

Edita el `.env` con tus credenciales mínimas:

```env
# LLM (requerido — elige uno)
GEMINI_API_KEY="tu-api-key-de-google-ai-studio"
MODEL="google/gemini-2.5-pro"

# WordPress (requerido para publicar)
WP_URL="https://tu-sitio-wordpress.com"
WP_USERNAME="tu-usuario-admin"
WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx"

# Imágenes (opcional)
FAL_KEY="tu-api-key-de-fal-ai"
```

> **¿Cómo obtener una WordPress Application Password?**  
> Panel WP → Usuarios → Tu perfil → sección "Contraseñas de aplicación" → Agregar.

---

## 3. Configurar categorías (opcional)

Edita `data/categories.json` para mapear nombres de categoría a sus IDs de WordPress:

```json
{
  "tecnologia": 5,
  "noticias": 12,
  "tutoriales": 8
}
```

> Para obtener los IDs de tus categorías, usa la tool `get_wordpress_categories` desde el cliente MCP.

---

## 4. Conectar al cliente MCP

### opencode (`~/.config/opencode/opencode.jsonc`)

```jsonc
{
  "mcp": {
    "wp_ai_content": {
      "type": "local",
      "command": ["python", "/ruta/al/proyecto/bridge/mcp_server.py"],
      "enabled": true
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "wp_ai_content": {
      "command": "python",
      "args": ["/ruta/al/proyecto/bridge/mcp_server.py"]
    }
  }
}
```

### openclaw

```json
{
  "mcp": {
    "servers": {
      "wp_ai_content": {
        "command": "python",
        "args": ["/ruta/al/proyecto/bridge/mcp_server.py"]
      }
    }
  }
}
```

> **Windows:** usa rutas con barras invertidas dobles o barras forward:  
> `"C:/Users/usuario/Desktop/wp_mcp_content_ai/bridge/mcp_server.py"`

---

## 5. Verificar que funciona

Ejecuta el servidor directamente para verificar que arranca sin errores:

```bash
python bridge/mcp_server.py
```

Deberías ver en stderr:
```
INFO:mcp_server:wp_ai_content MCP Server initializing…
INFO:mcp_server:wp_ai_content MCP Server ready — listening on stdio
```

El proceso queda en espera de stdin — eso es correcto, el cliente MCP se conectará a él.

---

## 6. Primera prueba desde el cliente

Una vez conectado al cliente MCP, puedes pedir:

```
Investiga el tema "inteligencia artificial en educación" en profundidad
```

El agente llamará automáticamente a `research_topic` y te devolverá hallazgos, tendencias, análisis competitivo y fuentes.

```
Genera un artículo de 1500 palabras sobre "blockchain y supply chain", 
con tono profesional para una audiencia de ejecutivos de logística.
Incluye las keywords: blockchain, trazabilidad, smart contracts.
```

---

## 7. Despliegue con Docker (Opcional)

Si prefieres aislar completamente el entorno y no instalar dependencias de Python de forma global o virtual en tu host, puedes empaquetar y ejecutar el servidor MCP en un contenedor de Docker local.

### 1. Construir la Imagen Docker
Ejecuta el siguiente comando en la raíz del proyecto para construir la imagen:
```bash
docker build -t wp_mcp_content_ai:latest .
```

### 2. Configurar el Cliente MCP con Docker
En lugar de llamar a `python`, configura tu cliente (Cursor, Claude Desktop, etc.) para que inicie el contenedor de Docker. 

Es **indispensable** usar el flag `-i` (modo interactivo) para que el cliente pueda comunicarse con el contenedor por stdio, cargar el archivo `.env` mediante `--env-file`, y mapear el volumen de datos con `-v` para persistir la base de datos JSON local.

#### Ejemplo de configuración (Claude Desktop / Cursor)
```json
{
  "mcpServers": {
    "wp_mcp_content_ai_docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "/RUTA/ABSOLUTA/A/.env",
        "-v",
        "/RUTA/ABSOLUTA/A/data:/app/data",
        "wp_mcp_content_ai:latest"
      ]
    }
  }
}
```

> **⚠️ Atención:** Reemplaza `/RUTA/ABSOLUTA/A/` con la ruta completa a la carpeta del proyecto en tu máquina (por ejemplo, `C:/Users/P0zcl/Desktop/wp_mcp_content_ai` en Windows).

---

## Solución de problemas comunes

| Error | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'mcp'` | Dependencias no instaladas | `pip install -r requirements.txt` |
| `GEMINI_API_KEY is not set` | `.env` no configurado | Asegúrate de tener el `.env` con la key |
| `WP REST Error 401` | Credenciales incorrectas | Verifica usuario y Application Password |
| `WP REST Error 404` | URL incorrecta | Verifica que `WP_URL` no tenga `/` al final |
| El servidor no aparece en el cliente | Ruta incorrecta | Usa la ruta absoluta al `bridge/mcp_server.py` o imagen Docker |
