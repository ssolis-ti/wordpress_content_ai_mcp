---
name: wp_mcp_content_ai
version: 1.1.0
description: AI-powered WordPress Content Generation, SEO Auditing, and Internal Linking MCP Server.
---

# WordPress AI Content System (wp_mcp_content_ai)

An AI-native Model Context Protocol (MCP) server and AgentSkill that automates the lifecycle of WordPress content: from research and SEO auditing to JSON-LD Schema generation, semantically-driven internal auto-linking, and publishing.

## 🏛️ System Requirements

- Python 3.10 or higher
- WordPress instance with REST API enabled and Application Passwords configured.
- API Keys for Google AI Studio (Gemini) and Fal.ai (Images).

## 🚀 Setup & Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

3. **Running the MCP Server:**
   Launch the server over standard input/output (stdio):
   ```bash
   python bridge/mcp_server.py
   ```

4. **Running Unit Tests:**
   Run the offline test suite to verify correct installation:
   ```bash
   python -m unittest tests/test_core.py
   ```

## 🛠️ MCP Tools Reference (13 Tools)

This server exposes 13 tools divided into 5 categories, enabling complete control over content creation, SEO, research, image generation, and WordPress management.

### Categoría: Contenido

#### 1. `generate_blog_post`
Generates a structured, SEO-optimized blog post in Markdown.
- **Parameters:**
  - `topic` (string, required): Main topic of the article.
  - `target_keywords` (array of strings, optional): Keywords to integrate (defaults to `[topic]`).
  - `word_count` (integer, optional): Target length, 100-10000 words (default: 1200).
  - `tone` (string, optional): Style: `professional` (default), `casual`, `authoritative`, `conversational`, `technical`, `persuasive`.
  - `target_audience` (string, optional): Target reader profile (default: `general`).

### Categoría: SEO y Semántica

#### 2. `seo_audit_and_optimize`
Performs a deterministic SEO audit on Markdown text and returns an LLM-optimized version.
- **Parameters:**
  - `content` (string, required): Markdown article text.
  - `primary_keyword` (string, required): Main target keyword.
  - `secondary_keywords` (array of strings, optional): Additional terms to verify.

#### 3. `audit_seo_entities`
Semantically audits DePIN, AI, and Web3 technical entities within the text.
- **Parameters:**
  - `content` (string, required): Content to analyze.
  - `topic` (string, required): Main topic.

#### 4. `inject_json_ld_schema`
Generates and injects Structured JSON-LD metadata markup (`TechArticle`) into a published WordPress post.
- **Parameters:**
  - `post_id` (integer, required): Target post ID.
  - `wp_url`, `username`, `app_password` (strings, required): Site credentials.

### Categoría: Investigación

#### 5. `research_topic`
Conducts topic and competitor research returning key findings, trends, and sources.
- **Parameters:**
  - `topic` (string, required): Topic to research.
  - `depth` (string, optional): `"basic"` (default) or `"comprehensive"`.

### Categoría: Publicación y Gestión (WordPress)

#### 6. `publish_to_wordpress`
Publishes a complete `BlogPost` object returned by `generate_blog_post` to WordPress.
- **Parameters:**
  - `content` (object, required): BlogPost dictionary.
  - `wp_url`, `username`, `app_password` (strings, required): Site credentials.
  - `status` (string, optional): `"draft"` (default) or `"publish"`.
  - `categories` (array of strings, optional): Resolved against `categories.json` or IDs.
  - `tags` (array of strings, optional).

#### 7. `create_wordpress_post`
Creates a post directly from a title and Markdown content without a `BlogPost` wrapper.
- **Parameters:**
  - `title`, `content`, `wp_url`, `username`, `app_password` (required).
  - `status` (string, optional): `"draft"` (default) or `"publish"`.
  - `categories`, `tags` (optional).

#### 8. `get_wordpress_posts`
Retrieves a paginated list of posts from the WordPress site.
- **Parameters:**
  - `wp_url`, `username`, `app_password` (required).
  - `per_page` (integer, optional): Posts to fetch, 1-100 (default: 10).
  - `page` (integer, optional): Page offset (default: 1).

#### 9. `get_wordpress_categories`
Retrieves all categories from the WordPress instance with their IDs, names, and slugs.
- **Parameters:**
  - `wp_url`, `username`, `app_password` (required).

#### 10. `update_wordpress_post`
Updates an existing WordPress post by ID (only updates provided fields).
- **Parameters:**
  - `post_id`, `wp_url`, `username`, `app_password` (required).
  - `title`, `content`, `status`, `slug`, `categories` (strings/arrays, optional).

### Categoría: SEO Técnico

#### 11. `suggest_internal_links`
Analyzes a post and suggests contextual internal linking opportunities from existing posts.
- **Parameters:**
  - `post_id`, `wp_url`, `username`, `app_password` (required).

#### 12. `apply_internal_links`
Calls suggestions and automatically applies contextual internal hyperlinks inside the post content.
- **Parameters:**
  - `post_id`, `wp_url`, `username`, `app_password` (required).

### Categoría: Imágenes

#### 13. `generate_image_asset`
Generates visual assets via Fal.ai (Flux/Schnell) or Pollinations.ai (fallback).
- **Parameters:**
  - `prompt` (string, required): Visual description.
  - `image_size` (string, optional): `"landscape_4_3"` (default), `"landscape_16_9"`, `"portrait_4_3"`, `"portrait_16_9"`, `"square"`.

## 🔌 Client Configuration

To register this server in Cursor or Claude Desktop, edit your config file (e.g., `claude_desktop_config.json` or `mcp_config.json`):

```json
{
  "mcpServers": {
    "wp_mcp_content_ai": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/wp_mcp_content_ai/bridge/mcp_server.py"]
    }
  }
}
```

> **Note:** The server loads credentials automatically from the `.env` file located in the project root, so there is no need to write secrets inside the client configuration file.

---
*Fidelity Status: NOMINAL | Built for Autonomous Agents.*
