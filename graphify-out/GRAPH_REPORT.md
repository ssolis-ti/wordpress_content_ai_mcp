# Graph Report - wordpress_content_ai_mcp  (2026-09-28)

## Corpus Check
- 34 files · ~27,836 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 3, .example 1)

## Summary
- 669 nodes · 1193 edges · 40 communities (36 shown, 4 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 76 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dae853eb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- tools.py
- models.py
- index.md
- WpContentAgent
- ContentGenerator
- mcp_server.py
- JSONStorage
- TestContentGenerator
- Componentes principales
- 🛠️ MCP Tools Reference (13 Tools)
- core.py
- call_llm
- BlogPost
- WordPress AI Content System (wp_mcp_content_ai)
- StorageManager
- Guía de Inicio Rápido
- SEOAuditor
- ImageGenerator
- ContentGeneratorEngine
- BaseModel
- SEOScore
- WordPress AI Content System - Application Context
- WordPress Content System Agent (Portero)
- Core Capabilities
- Future Enhancements (Planned)
- WordPress Integration
- Usage Guidelines
- SEO Features
- Workflow Examples
- Configuration Options
- Content Generation Features
- Performance Considerations
- Error Handling
- System Architecture
- Research Capabilities
- app/__init__.py
- .test_generate_blog_post_invalid_tone
- .test_research_topic_comprehensive
- .tearDown

## God Nodes (most connected - your core abstractions)
1. `ContentGenerator` - 38 edges
2. `BlogPost` - 35 edges
3. `TestContentGenerator` - 34 edges
4. `ContentMetadata` - 26 edges
5. `SEOScore` - 23 edges
6. `WpContentAgent` - 22 edges
7. `call_tool()` - 21 edges
8. `call_llm()` - 17 edges
9. `ContentTone` - 17 edges
10. `SEOAuditor` - 17 edges

## Surprising Connections (you probably didn't know these)
- `1. Mocking Dinámico de LLM (`call_llm`)` --references--> `call_llm()`  [INFERRED]
  docs/verification-qa.md → app/llm.py
- `6. `publish_to_wordpress`` --references--> `BlogPost`  [INFERRED]
  SKILL.md → app/models.py
- ``bridge/mcp_server.py` — Capa MCP` --references--> `call_tool()`  [INFERRED]
  docs/architecture.md → bridge/mcp_server.py
- `13. `generate_image_asset`` --references--> `generate_image_asset()`  [INFERRED]
  SKILL.md → portero/tools.py
- `🔄 Capa de Retrocompatibilidad de la Fachada` --references--> `ContentGenerator`  [INFERRED]
  docs/verification-qa.md → app/core.py

## Import Cycles
- None detected.

## Communities (40 total, 4 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (60): argparse, ask_porter_simple(), ask_porter_simple_chat(), ask_portero(), ask_portero_batch(), ask_portero_with_context(), clear_agent_memory(), get_agent_status() (+52 more)

### Community 1 - "tools.py"
Cohesion: 0.05
Nodes (50): 10. `inject_json_ld_schema`, 11. `suggest_internal_links`, 12. `apply_internal_links`, 13. `generate_image_asset`, 1. `generate_blog_post`, 2. `seo_audit_and_optimize`, 3. `audit_seo_entities`, 4. `research_topic` (+42 more)

### Community 2 - "models.py"
Cohesion: 0.06
Nodes (38): ContentStatus, ContentTone, Data models for WordPress AI Content system., Available content tones., Result of WordPress publishing., Content status for WordPress., Results of SEO audit and optimization., SEOAuditResult (+30 more)

### Community 3 - "index.md"
Cohesion: 0.05
Nodes (35): Comportamiento sin el archivo, Configuración, Cómo obtener los IDs de tus categorías, `data/categories.json`, Ejemplo de `.env` completo, Flujo de selección del modelo LLM, Formato, Identidad del sitio — JSON-LD Schema (+27 more)

### Community 4 - "WpContentAgent"
Cohesion: 0.07
Nodes (24): Agent, LiteLLMProxy, MemoryManager, Any, Main agent for WordPress AI Content system., Initialize the WordPress content agent. Args: config_path: Optional path to…, Load configuration from file or use defaults., Initialize LiteLLM proxy. (+16 more)

### Community 5 - "ContentGenerator"
Cohesion: 0.07
Nodes (17): ContentGenerator, Any, Retrieve a paginated list of posts from WordPress., Create a simple WordPress post from plain markdown (no BlogPost object needed)., Facade core content generation engine., SEO recommendation item., SEORecommendation, 1. Mocking Dinámico de LLM (`call_llm`) (+9 more)

### Community 6 - "mcp_server.py"
Cohesion: 0.19
Nodes (29): asyncio, _apply_internal_links(), _audit_seo_entities(), call_tool(), _create_wordpress_post(), _err(), _generate_blog_post(), _generate_image_asset() (+21 more)

### Community 7 - "JSONStorage"
Cohesion: 0.10
Nodes (16): JSONStorage, Any, Get item by ID. Args: item_id: Item ID Returns: Item if found, None otherwise, Get all items. Returns: List of all items, Update existing item. Args: item_id: Item ID item: Updated item Returns: True…, Delete item by ID. Args: item_id: Item ID Returns: True if successful, False…, Search items by field values. Args: **kwargs: Field name and value pairs to…, Generic JSON storage class for different data types. (+8 more)

### Community 8 - "TestContentGenerator"
Cohesion: 0.07
Nodes (15): Test generating a blog post with valid parameters., Test generating a blog post with empty topic., Test generating a blog post with invalid word count., Test performing SEO audit with valid content., Test performing SEO audit with empty content., Test performing SEO audit with empty primary keyword., Test researching a topic with valid parameters., Test cases for ContentGenerator class. (+7 more)

### Community 9 - "Componentes principales"
Cohesion: 0.08
Nodes (23): get_content_generator(), Get or create global content generator instance., _parse_tone(), Convert a tone string to ContentTone enum with fallback to PROFESSIONAL., `app/core.py` — Fachada, `app/generator.py` — Motor de Contenido, `app/llm.py` — Cliente LLM, `app/models.py` — Modelos de datos (+15 more)

### Community 10 - "🛠️ MCP Tools Reference (13 Tools)"
Cohesion: 0.08
Nodes (23): 10. `update_wordpress_post`, 11. `suggest_internal_links`, 12. `apply_internal_links`, 13. `generate_image_asset`, 1. `generate_blog_post`, 2. `seo_audit_and_optimize`, 3. `audit_seo_entities`, 4. `inject_json_ld_schema` (+15 more)

### Community 11 - "core.py"
Cohesion: 0.18
Nodes (15): Core Facade interface for WordPress AI Content system., Blog post content generation engine for WordPress AI Content system., Image generation engine using fal.ai for WordPress AI Content system., LLM completion interface using LiteLLM with built-in resilience and backup…, Topic research engine for WordPress AI Content system., SEO audit and entity analysis engine for WordPress AI Content system., fal_client, json (+7 more)

### Community 12 - "call_llm"
Cohesion: 0.17
Nodes (14): call_llm(), Call LiteLLM with configured model, API keys, and exponential backoff retry.…, Results of topic research., ResearchResult, Any, Generate relevant reference sources using the LLM., Generate actionable content recommendations based on research findings., Core topic research engine — all data generated by the LLM. (+6 more)

### Community 13 - "BlogPost"
Cohesion: 0.15
Nodes (13): BlogPost, ContentMetadata, Metadata for generated content., Complete blog post model., patch, Test publishing to WordPress with valid parameters., Test publishing to WordPress with empty URL., Test publishing to WordPress with invalid status. (+5 more)

### Community 14 - "WordPress AI Content System (wp_mcp_content_ai)"
Cohesion: 0.11
Nodes (18): 1. Claude Desktop o Cursor (mcpConfig.json), 1. Google Gemini (Recomendado por defecto), 2. OpenAI (GPT), 2. opencode (~/.config/opencode/opencode.jsonc), 3. Anthropic (Claude), 3. openclaw (openclaw.json), 4. Ollama (100% Local y Gratis), A. Ejecución con Python Local (+10 more)

### Community 15 - "StorageManager"
Cohesion: 0.13
Nodes (11): get_storage_manager(), Path, Main storage manager for the application., Initialize storage manager. Args: data_path: Path to data directory, Get blog post by title. Args: title: Blog post title Returns: BlogPost if…, Get blog posts containing specific keyword. Args: keyword: Keyword to search…, Get most recent blog posts. Args: limit: Maximum number of posts to return…, Get SEO audits for a specific blog post. Args: post_id: Blog post ID Returns:… (+3 more)

### Community 16 - "Guía de Inicio Rápido"
Cohesion: 0.12
Nodes (16): 1. Construir la Imagen Docker, 1. Instalación, 2. Configuración del entorno, 2. Configurar el Cliente MCP con Docker, 3. Configurar categorías (opcional), 4. Conectar al cliente MCP, 5. Verificar que funciona, 6. Primera prueba desde el cliente (+8 more)

### Community 17 - "SEOAuditor"
Cohesion: 0.19
Nodes (8): Any, Core SEO auditing and entity analysis engine., Generate prioritized SEO recommendations based on actual metrics., Perform comprehensive SEO analysis and optimization on content., Use the LLM to apply SEO recommendations to the content., Realiza una auditoría semántica de entidades técnicas., Calculate a real SEO score from deterministic text metrics., SEOAuditor

### Community 18 - "ImageGenerator"
Cohesion: 0.23
Nodes (8): ImageGenerator, Generate an image using fal.ai with automatic prompt enhancement, negative…, Image generation engine using fal.ai with integrated HIFI prompt enhancement., Simulate image generation when API is unavailable., Initialize image generator., Enrich a basic prompt with premium technical and cinematic aesthetic modifiers., GeneratedImage, Model for generated image asset.

### Community 19 - "ContentGeneratorEngine"
Cohesion: 0.22
Nodes (7): Path, Initialize content generator., ContentGeneratorEngine, Generate an SEO-friendly meta description using the LLM., Generate a URL-friendly slug from a topic string., Core blog post generation engine., Generate a complete SEO-optimized blog post.

### Community 20 - "BaseModel"
Cohesion: 0.20
Nodes (7): Request for publishing to WordPress., Validate WordPress URL format., Ensure slug is URL-friendly., Ensure word count is reasonable., WordPressPublishRequest, BaseModel, validator

### Community 21 - "SEOScore"
Cohesion: 0.25
Nodes (6): SEOScore, main(), publish_to_wordpress(), Publish content to WordPress. Args: content: BlogPost content dictionary (from…, Test SEO recommendations generation., Test SEOScore model validation.

### Community 22 - "WordPress AI Content System - Application Context"
Cohesion: 0.29
Nodes (6): Common Issues, Conclusion, Getting Help, Overview, Support and Troubleshooting, WordPress AI Content System - Application Context

### Community 23 - "WordPress Content System Agent (Portero)"
Cohesion: 0.29
Nodes (6): Example Dialogue, Guidelines, Interaction Style, Mission, Tools, WordPress Content System Agent (Portero)

### Community 24 - "Core Capabilities"
Cohesion: 0.40
Nodes (5): 1. Content Generation, 2. SEO Audit and Optimization, 3. Topic Research, 4. WordPress Publishing, Core Capabilities

### Community 25 - "Future Enhancements (Planned)"
Cohesion: 0.40
Nodes (5): Content Features, Future Enhancements (Planned), Integration Features, SEO Features, WordPress Features

### Community 26 - "WordPress Integration"
Cohesion: 0.50
Nodes (4): Authentication, Content Mapping, Publishing Options, WordPress Integration

### Community 27 - "Usage Guidelines"
Cohesion: 0.50
Nodes (4): Best Practices, Common Use Cases, Integration Scenarios, Usage Guidelines

### Community 28 - "SEO Features"
Cohesion: 0.50
Nodes (4): Best Practices Implemented, Optimization Recommendations, Scoring System, SEO Features

### Community 29 - "Workflow Examples"
Cohesion: 0.50
Nodes (4): Complete Content Creation Pipeline, Content Optimization Only, Quick Publishing Workflow, Workflow Examples

### Community 30 - "Configuration Options"
Cohesion: 0.50
Nodes (4): Configuration Options, Content Settings, LLM Settings, Portero Agent Settings

### Community 31 - "Content Generation Features"
Cohesion: 0.50
Nodes (4): Content Generation Features, Multimedia Integration, Structure Elements, Tone Options

### Community 32 - "Performance Considerations"
Cohesion: 0.50
Nodes (4): Content Quality, Performance Considerations, Processing Speed, Scalability

### Community 33 - "Error Handling"
Cohesion: 0.50
Nodes (4): Error Handling, Runtime Errors, User-Friendly Messages, Validation Errors

### Community 34 - "System Architecture"
Cohesion: 0.67
Nodes (3): Core Components, Data Models, System Architecture

### Community 35 - "Research Capabilities"
Cohesion: 0.67
Nodes (3): Depth Levels, Research Capabilities, Research Components

## Knowledge Gaps
- **134 isolated node(s):** `Colors`, `Opción A: Ejecución Nativa (Local)`, `Opción B: Ejecución Aislada con Docker (Opcional)`, `1. Google Gemini (Recomendado por defecto)`, `2. OpenAI (GPT)` (+129 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 350 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BlogPost` connect `BlogPost` to `tools.py`, `models.py`, `ContentGenerator`, `mcp_server.py`, `TestContentGenerator`, `🛠️ MCP Tools Reference (13 Tools)`, `core.py`, `StorageManager`, `ContentGeneratorEngine`, `BaseModel`, `SEOScore`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `Verificación y Control de Calidad (QA)` connect `ContentGenerator` to `index.md`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `ContentGenerator` connect `ContentGenerator` to `tools.py`, `models.py`, `TestContentGenerator`, `Componentes principales`, `core.py`, `call_llm`, `BlogPost`, `SEOAuditor`, `ContentGeneratorEngine`, `SEOScore`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `ContentGenerator` (e.g. with `ContentGeneratorEngine` and `BlogPost`) actually correct?**
  _`ContentGenerator` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `BlogPost` (e.g. with `ContentGenerator` and `ContentGeneratorEngine`) actually correct?**
  _`BlogPost` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TestContentGenerator` (e.g. with `ContentGenerator` and `BlogPost`) actually correct?**
  _`TestContentGenerator` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ContentMetadata` (e.g. with `ContentGeneratorEngine` and `🛡️ Auditoría de Robustez y Mejoras Introducidas`) actually correct?**
  _`ContentMetadata` has 5 INFERRED edges - model-reasoned connections that need verification._