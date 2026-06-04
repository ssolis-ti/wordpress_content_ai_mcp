# WordPress AI Content System (wp_mcp_content_ai)

> Servidor MCP (Model Context Protocol) escrito en Python que automatiza todo el ciclo de vida del contenido en WordPress: investigación de temas, redacción con IA, auditorías SEO en tiempo real, enlazado interno automático e inyección de datos estructurados JSON-LD.

---

## 🚀 Instalación y Despliegue Rápido

Tienes dos opciones para ejecutar y configurar este servidor MCP localmente:

### Opción A: Ejecución Nativa (Local)

1. **Clona el repositorio e instala dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Crea tu archivo de entorno:**
   ```bash
   cp .env.example .env
   ```
3. **Ejecuta el servidor:**
   ```bash
   python bridge/mcp_server.py
   ```

### Opción B: Ejecución Aislada con Docker (Opcional)

Si prefieres no instalar Python ni dependencias en tu máquina:

1. **Construye la imagen de Docker:**
   ```bash
   docker build -t wp_mcp_content_ai:latest .
   ```
2. **Conecta tu cliente MCP apuntando a la ejecución de Docker:**
   Ver configuración de clientes abajo.

---

## 🧠 Configuración de las IAs (Proveedores LLM)

El sistema utiliza **LiteLLM** bajo el capó. Para cambiar de modelo o proveedor, edita las siguientes variables en tu archivo `.env`:

### 1. Google Gemini (Recomendado por defecto)
* **Variable `MODEL`**: `google/gemini-2.5-pro` o `gemini/gemini-flash-latest`
* **Configuración `.env`**:
  ```env
  MODEL="google/gemini-2.5-pro"
  GEMINI_API_KEY="tu-api-key-de-google-ai-studio"
  ```

### 2. OpenAI (GPT)
* **Variable `MODEL`**: `gpt-4o` o `gpt-4o-mini`
* **Configuración `.env`**:
  ```env
  MODEL="gpt-4o"
  OPENAI_API_KEY="tu-api-key-de-openai"
  ```

### 3. Anthropic (Claude)
* **Variable `MODEL`**: `anthropic/claude-3-5-sonnet-20241022`
* **Configuración `.env`**:
  ```env
  MODEL="anthropic/claude-3-5-sonnet-20241022"
  ANTHROPIC_API_KEY="tu-api-key-de-anthropic"
  ```

### 4. Ollama (100% Local y Gratis)
* **Variable `MODEL`**: `ollama/tu-modelo-descargado` (ej. `ollama/llama3` o `ollama/gemma2`)
* **Configuración `.env`**:
  ```env
  MODEL="ollama/llama3"
  OPENAI_API_BASE="http://localhost:11434"
  ```

---

## 🎨 Generación de Imágenes para Artículos

El sistema incluye soporte de generación de imágenes destacadas para tus publicaciones de WordPress:

1. **Generación con Fal.ai (Calidad de Producción - Flux/Schnell):**
   Para generar imágenes realistas e ilustraciones de alta fidelidad, obtén una key en [fal.ai](https://fal.ai) y configúrala en tu `.env`:
   ```env
   FAL_KEY="tu-api-key-de-fal-ai"
   ```
2. **Generación Gratuita / Fallback (Pollinations.ai):**
   Si **no** configuras `FAL_KEY` en tu `.env`, el sistema **no fallará**. En su lugar, utilizará **Pollinations.ai** de forma automática y transparente para retornar una URL de previsualización de imagen completamente gratuita e ilimitada.

---

## 🔌 Integración con Clientes MCP

Añade el servidor a tu cliente de IA preferido. Recuerda reemplazar `/RUTA/ABSOLUTA/A/` con la ruta completa a la carpeta del proyecto en tu máquina.

### A. Ejecución con Python Local

#### 1. Claude Desktop o Cursor (mcpConfig.json)
```json
{
  "mcpServers": {
    "wp_mcp_content_ai": {
      "command": "python",
      "args": ["/RUTA/ABSOLUTA/A/wp_mcp_content_ai/bridge/mcp_server.py"]
    }
  }
}
```

#### 2. opencode (~/.config/opencode/opencode.jsonc)
```jsonc
{
  "mcp": {
    "wp_mcp_content_ai": {
      "type": "local",
      "command": ["python", "/RUTA/ABSOLUTA/A/wp_mcp_content_ai/bridge/mcp_server.py"],
      "enabled": true
    }
  }
}
```

#### 3. openclaw (openclaw.json)
```json
{
  "mcp": {
    "servers": {
      "wp_mcp_content_ai": {
        "command": "python",
        "args": ["/RUTA/ABSOLUTA/A/wp_mcp_content_ai/bridge/mcp_server.py"]
      }
    }
  }
}
```

---

### B. Ejecución con Docker (Opcional)

Si utilizas la imagen construida de Docker, configura tu cliente para levantar el contenedor:

#### Claude Desktop o Cursor (mcpConfig.json)
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
        "/RUTA/ABSOLUTA/A/wp_mcp_content_ai/.env",
        "-v",
        "/RUTA/ABSOLUTA/A/wp_mcp_content_ai/data:/app/data",
        "wp_mcp_content_ai:latest"
      ]
    }
  }
}
```

---

## 📚 Índice de Documentación Detallada

Para más información, consulta la documentación del proyecto dentro de la carpeta `docs/`:

* [📖 Guía de Inicio Rápido](docs/getting-started.md)
* [🔧 Referencia Completa de las 13 Tools MCP](docs/mcp-tools.md)
* [⚙️ Guía de Variables y Categorías (`categories.json`)](docs/configuration.md)
* [🏗️ Arquitectura en Capas y Patrones de Diseño](docs/architecture.md)
* [🧪 Plan de Verificación y Testing Offline](docs/verification-qa.md)
* [🛡️ Identidad e Instrucciones del Agente (Portero)](docs/PORTERO.md)
