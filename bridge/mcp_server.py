"""MCP Server for WordPress AI Content System.

Exposes content generation, SEO, research, and WordPress publishing
capabilities as MCP tools consumable by any MCP-compatible client
(Claude Desktop, opencode, openclaw, Cursor, etc.).

Transport: stdio (standard MCP local server pattern)
API: mcp >= 1.0.0 using list_tools / call_tool handler pattern
"""

import asyncio
import json
import logging
import sys
import os
from dotenv import load_dotenv

# Load .env FIRST — before any app imports that might need API keys
load_dotenv()

# Configure logging to stderr so it doesn't pollute the MCP stdio stream
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_server")

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# Import core engine as singleton — initialized once, reused across all tool calls
from app.core import get_content_generator

_generator = get_content_generator()

# Initialize the MCP Server
server = Server("wp_ai_content")

logger.info("wp_ai_content MCP Server initializing…")


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _ok(data: dict) -> list[TextContent]:
    """Return a successful JSON TextContent response."""
    return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]


def _err(message: str, detail: str = "") -> list[TextContent]:
    """Return an error JSON TextContent response."""
    payload = {"success": False, "error": message}
    if detail:
        payload["detail"] = detail
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


# ---------------------------------------------------------------------------
# Tool definitions (schemas)
# ---------------------------------------------------------------------------

TOOLS = [
    Tool(
        name="generate_blog_post",
        description=(
            "Generate a full SEO-optimized blog post in Markdown from a topic and keywords. "
            "Returns title, content, meta_description, slug, seo_score, tags, reading_time_minutes."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Main subject of the article (required)."},
                "target_keywords": {"type": "array", "items": {"type": "string"}, "description": "SEO keywords to include. Defaults to [topic]."},
                "word_count": {"type": "integer", "default": 1200, "description": "Target word count (100–10000). Default: 1200."},
                "tone": {"type": "string", "default": "professional", "description": "Writing style: professional, casual, authoritative, conversational, technical, persuasive."},
                "target_audience": {"type": "string", "default": "general", "description": "Intended reader, e.g. 'developers' or 'crypto investors'."},
            },
            "required": ["topic"],
        },
    ),
    Tool(
        name="seo_audit_and_optimize",
        description=(
            "Perform a comprehensive SEO audit on existing Markdown content and return an optimized version. "
            "Calculates real scores for keyword density, readability, heading structure, and secondary keyword coverage."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Article text in Markdown format (required)."},
                "primary_keyword": {"type": "string", "description": "Main target keyword for SEO (required)."},
                "secondary_keywords": {"type": "array", "items": {"type": "string"}, "description": "Additional keywords to check."},
            },
            "required": ["content", "primary_keyword"],
        },
    ),
    Tool(
        name="audit_seo_entities",
        description=(
            "Perform a semantic entity audit for DePIN/AI/Web3 content. "
            "Identifies present and missing technical entities with integration recommendations."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Full article text to analyze."},
                "topic": {"type": "string", "description": "Main topic of the article."},
            },
            "required": ["content", "topic"],
        },
    ),
    Tool(
        name="research_topic",
        description=(
            "Conduct LLM-powered research on a topic. "
            "Returns key findings, trends, competitor analysis, sources, and content recommendations."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to research (required)."},
                "depth": {"type": "string", "default": "basic", "description": "'basic' (5 findings, 3 trends) or 'comprehensive' (8 findings, 5 trends)."},
            },
            "required": ["topic"],
        },
    ),
    Tool(
        name="publish_to_wordpress",
        description=(
            "Publish a generated blog post to WordPress via REST API. "
            "Use 'draft' status for review before publishing live."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "object", "description": "BlogPost dict returned by generate_blog_post (required)."},
                "wp_url": {"type": "string", "description": "WordPress site URL, e.g. 'https://yoursite.com' (required)."},
                "username": {"type": "string", "description": "WordPress admin username (required)."},
                "app_password": {"type": "string", "description": "WordPress Application Password (required). Generate at: WP Admin → Users → Profile → Application Passwords."},
                "status": {"type": "string", "default": "draft", "description": "'draft' (default) or 'publish'."},
                "categories": {"type": "array", "items": {"type": "string"}, "description": "Category names or IDs."},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tag strings."},
            },
            "required": ["content", "wp_url", "username", "app_password"],
        },
    ),
    Tool(
        name="create_wordpress_post",
        description=(
            "Create a WordPress post directly from a title and Markdown string, "
            "without going through the full generate_blog_post flow."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Post title (required)."},
                "content": {"type": "string", "description": "Post body in Markdown (required)."},
                "wp_url": {"type": "string", "description": "WordPress site URL (required)."},
                "username": {"type": "string", "description": "WordPress username (required)."},
                "app_password": {"type": "string", "description": "WordPress Application Password (required)."},
                "status": {"type": "string", "default": "draft", "description": "'draft' or 'publish'."},
                "categories": {"type": "array", "items": {"type": "string"}},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "content", "wp_url", "username", "app_password"],
        },
    ),
    Tool(
        name="get_wordpress_posts",
        description=(
            "Retrieve a paginated list of posts from WordPress. "
            "Useful for finding post IDs before updating or providing context for internal link suggestions."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "wp_url": {"type": "string", "description": "WordPress site URL (required)."},
                "username": {"type": "string", "description": "WordPress username (required)."},
                "app_password": {"type": "string", "description": "WordPress Application Password (required)."},
                "per_page": {"type": "integer", "default": 10, "description": "Posts per page (1–100)."},
                "page": {"type": "integer", "default": 1, "description": "Page number."},
            },
            "required": ["wp_url", "username", "app_password"],
        },
    ),
    Tool(
        name="get_wordpress_categories",
        description="Retrieve all categories from the WordPress site with their IDs, names, slugs, and post counts.",
        inputSchema={
            "type": "object",
            "properties": {
                "wp_url": {"type": "string", "description": "WordPress site URL (required)."},
                "username": {"type": "string", "description": "WordPress username (required)."},
                "app_password": {"type": "string", "description": "WordPress Application Password (required)."},
            },
            "required": ["wp_url", "username", "app_password"],
        },
    ),
    Tool(
        name="update_wordpress_post",
        description=(
            "Update an existing WordPress post by ID. "
            "Only provide the fields you want to change; others are left untouched."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "post_id": {"type": "integer", "description": "WordPress post ID (required)."},
                "wp_url": {"type": "string", "description": "WordPress site URL (required)."},
                "username": {"type": "string", "description": "WordPress username (required)."},
                "app_password": {"type": "string", "description": "WordPress Application Password (required)."},
                "title": {"type": "string", "description": "New title (optional)."},
                "content": {"type": "string", "description": "New content in Markdown (optional)."},
                "status": {"type": "string", "description": "New status: 'draft', 'publish', 'pending', 'private' (optional)."},
                "slug": {"type": "string", "description": "New URL slug (optional)."},
                "categories": {"type": "array", "items": {"type": "string"}, "description": "New categories (optional)."},
            },
            "required": ["post_id", "wp_url", "username", "app_password"],
        },
    ),
    Tool(
        name="inject_json_ld_schema",
        description=(
            "Inject TechArticle JSON-LD structured data into an existing WordPress post. "
            "Improves Google rich results eligibility and semantic authority."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "post_id": {"type": "integer", "description": "WordPress post ID (required)."},
                "wp_url": {"type": "string", "description": "WordPress site URL (required)."},
                "username": {"type": "string", "description": "WordPress username (required)."},
                "app_password": {"type": "string", "description": "WordPress Application Password (required)."},
            },
            "required": ["post_id", "wp_url", "username", "app_password"],
        },
    ),
    Tool(
        name="suggest_internal_links",
        description=(
            "Suggest contextual internal links for a post based on other published articles. "
            "Analyzes the target post and compares against recent posts to find anchor text opportunities."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "post_id": {"type": "integer", "description": "WordPress post ID to enrich (required)."},
                "wp_url": {"type": "string", "description": "WordPress site URL (required)."},
                "username": {"type": "string", "description": "WordPress username (required)."},
                "app_password": {"type": "string", "description": "WordPress Application Password (required)."},
            },
            "required": ["post_id", "wp_url", "username", "app_password"],
        },
    ),
    Tool(
        name="apply_internal_links",
        description=(
            "Automatically suggest and apply contextual internal links to a WordPress post. "
            "Only replaces the FIRST occurrence of each anchor text. Skips already-linked anchors."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "post_id": {"type": "integer", "description": "WordPress post ID to update (required)."},
                "wp_url": {"type": "string", "description": "WordPress site URL (required)."},
                "username": {"type": "string", "description": "WordPress username (required)."},
                "app_password": {"type": "string", "description": "WordPress Application Password (required)."},
            },
            "required": ["post_id", "wp_url", "username", "app_password"],
        },
    ),
    Tool(
        name="generate_image_asset",
        description=(
            "Generate a high-quality image asset using fal.ai (flux/schnell model). "
            "Known DePIN/crypto entities receive precise visual descriptions automatically. "
            "If FAL_KEY is not set, returns a Pollinations.ai preview URL."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Description of the image to generate (required)."},
                "image_size": {
                    "type": "string",
                    "default": "landscape_4_3",
                    "description": "Output dimensions: 'landscape_4_3' (default), 'square', 'portrait_4_3', 'landscape_16_9', 'portrait_16_9'.",
                },
            },
            "required": ["prompt"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool list handler
# ---------------------------------------------------------------------------

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return the list of all available tools."""
    return TOOLS


# ---------------------------------------------------------------------------
# Tool call dispatcher
# ---------------------------------------------------------------------------

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch tool calls to the appropriate handler."""
    try:
        if name == "generate_blog_post":
            return await _generate_blog_post(arguments)
        elif name == "seo_audit_and_optimize":
            return await _seo_audit_and_optimize(arguments)
        elif name == "audit_seo_entities":
            return await _audit_seo_entities(arguments)
        elif name == "research_topic":
            return await _research_topic(arguments)
        elif name == "publish_to_wordpress":
            return await _publish_to_wordpress(arguments)
        elif name == "create_wordpress_post":
            return await _create_wordpress_post(arguments)
        elif name == "get_wordpress_posts":
            return await _get_wordpress_posts(arguments)
        elif name == "get_wordpress_categories":
            return await _get_wordpress_categories(arguments)
        elif name == "update_wordpress_post":
            return await _update_wordpress_post(arguments)
        elif name == "inject_json_ld_schema":
            return await _inject_json_ld_schema(arguments)
        elif name == "suggest_internal_links":
            return await _suggest_internal_links(arguments)
        elif name == "apply_internal_links":
            return await _apply_internal_links(arguments)
        elif name == "generate_image_asset":
            return await _generate_image_asset(arguments)
        else:
            return _err(f"Unknown tool: {name}")
    except Exception as e:
        logger.exception(f"Unexpected error dispatching tool '{name}'")
        return _err(f"Server error in tool '{name}'", str(e))


# ---------------------------------------------------------------------------
# Individual tool handlers
# ---------------------------------------------------------------------------

async def _generate_blog_post(args: dict) -> list[TextContent]:
    try:
        result = _generator.generate_blog_post(
            topic=args["topic"],
            target_keywords=args.get("target_keywords"),
            word_count=args.get("word_count", 1200),
            tone=args.get("tone", "professional"),
            target_audience=args.get("target_audience", "general"),
        )
        return _ok({
            "success": True,
            "title": result.metadata.title,
            "content": result.content,
            "meta_description": result.metadata.meta_description,
            "slug": result.metadata.slug,
            "word_count": result.word_count,
            "reading_time_minutes": result.metadata.reading_time_minutes,
            "tone": result.tone.value if hasattr(result.tone, "value") else str(result.tone),
            "target_audience": result.target_audience,
            "target_keywords": result.target_keywords,
            "categories": result.metadata.categories,
            "tags": result.metadata.tags,
            "images_suggestions": result.images_suggestions,
            "seo_score": result.seo_score.model_dump() if result.seo_score else None,
        })
    except ValueError as e:
        return _err("Validation error", str(e))
    except RuntimeError as e:
        return _err("Content generation failed", str(e))
    except Exception as e:
        logger.exception("Error in generate_blog_post")
        return _err("Unexpected error", str(e))


async def _seo_audit_and_optimize(args: dict) -> list[TextContent]:
    try:
        result = _generator.seo_audit_and_optimize(
            content=args["content"],
            primary_keyword=args["primary_keyword"],
            secondary_keywords=args.get("secondary_keywords"),
        )
        return _ok({
            "success": True,
            "seo_score": result.seo_score.model_dump(),
            "recommendations": [r.model_dump() for r in result.recommendations],
            "optimized_content": result.optimized_content,
            "improvements_summary": result.improvements_summary,
            "primary_keyword": result.primary_keyword,
            "secondary_keywords": result.secondary_keywords,
            "total_recommendations": len(result.recommendations),
        })
    except ValueError as e:
        return _err("Validation error", str(e))
    except RuntimeError as e:
        return _err("SEO audit failed", str(e))
    except Exception as e:
        logger.exception("Error in seo_audit_and_optimize")
        return _err("Unexpected error", str(e))


async def _audit_seo_entities(args: dict) -> list[TextContent]:
    try:
        result = _generator.audit_seo_entities(args["content"], args["topic"])
        return _ok(result)
    except Exception as e:
        logger.exception("Error in audit_seo_entities")
        return _err("Entity audit failed", str(e))


async def _research_topic(args: dict) -> list[TextContent]:
    try:
        result = _generator.research_topic(
            topic=args["topic"],
            depth=args.get("depth", "basic"),
        )
        return _ok({
            "success": True,
            "topic": result.topic,
            "depth": result.depth,
            "key_findings": result.key_findings,
            "trends": result.trends,
            "competitor_analysis": result.competitor_analysis,
            "sources": result.sources,
            "recommendations": result.recommendations,
        })
    except ValueError as e:
        return _err("Validation error", str(e))
    except RuntimeError as e:
        return _err("Research failed", str(e))
    except Exception as e:
        logger.exception("Error in research_topic")
        return _err("Unexpected error", str(e))


async def _publish_to_wordpress(args: dict) -> list[TextContent]:
    try:
        from app.models import BlogPost, ContentMetadata, ContentTone, SEOScore

        content = args["content"]
        metadata = ContentMetadata(
            title=content.get("title", ""),
            meta_description=content.get("meta_description", ""),
            slug=content.get("slug", ""),
            reading_time_minutes=content.get("reading_time_minutes", 5),
            categories=content.get("categories", []),
            tags=content.get("tags", []),
        )
        seo_score = None
        if content.get("seo_score"):
            seo_score = SEOScore(**content["seo_score"])

        blog_post = BlogPost(
            metadata=metadata,
            content=content.get("content", ""),
            tone=ContentTone(content.get("tone", "professional")),
            target_audience=content.get("target_audience", "general"),
            word_count=max(100, content.get("word_count", 500)),
            target_keywords=content.get("target_keywords", []),
            seo_score=seo_score,
            seo_recommendations=[],
            images_suggestions=content.get("images_suggestions", []),
        )

        result = _generator.publish_to_wordpress(
            content=blog_post,
            wp_url=args["wp_url"],
            username=args["username"],
            app_password=args["app_password"],
            status=args.get("status", "draft"),
            categories=args.get("categories"),
            tags=args.get("tags"),
        )
        return _ok({
            "success": result.success,
            "post_id": result.post_id,
            "post_url": result.post_url,
            "published_at": result.published_at.isoformat() if result.published_at else None,
            "status": args.get("status", "draft"),
            "error": result.error_message,
        })
    except ValueError as e:
        return _err("Validation error", str(e))
    except Exception as e:
        logger.exception("Error in publish_to_wordpress")
        return _err("Publishing failed", str(e))


async def _create_wordpress_post(args: dict) -> list[TextContent]:
    try:
        result = _generator.create_simple_wordpress_post(
            title=args["title"],
            content=args["content"],
            wp_url=args["wp_url"],
            username=args["username"],
            app_password=args["app_password"],
            status=args.get("status", "draft"),
        )
        return _ok(result)
    except Exception as e:
        logger.exception("Error in create_wordpress_post")
        return _err("Post creation failed", str(e))


async def _get_wordpress_posts(args: dict) -> list[TextContent]:
    try:
        result = _generator.get_wordpress_posts(
            wp_url=args["wp_url"],
            username=args["username"],
            app_password=args["app_password"],
            per_page=args.get("per_page", 10),
            page=args.get("page", 1),
        )
        return _ok(result)
    except Exception as e:
        logger.exception("Error in get_wordpress_posts")
        return _err("Failed to retrieve posts", str(e))


async def _get_wordpress_categories(args: dict) -> list[TextContent]:
    try:
        result = _generator.get_wordpress_categories(
            args["wp_url"], args["username"], args["app_password"]
        )
        return _ok(result)
    except Exception as e:
        logger.exception("Error in get_wordpress_categories")
        return _err("Failed to retrieve categories", str(e))


async def _update_wordpress_post(args: dict) -> list[TextContent]:
    try:
        result = _generator.update_wordpress_post(
            post_id=args["post_id"],
            wp_url=args["wp_url"],
            username=args["username"],
            app_password=args["app_password"],
            title=args.get("title"),
            content=args.get("content"),
            status=args.get("status"),
            slug=args.get("slug"),
            categories=args.get("categories"),
        )
        return _ok(result)
    except Exception as e:
        logger.exception("Error in update_wordpress_post")
        return _err("Post update failed", str(e))


async def _inject_json_ld_schema(args: dict) -> list[TextContent]:
    try:
        result = _generator.inject_json_ld_schema(
            args["post_id"], args["wp_url"], args["username"], args["app_password"]
        )
        return _ok(result)
    except Exception as e:
        logger.exception("Error in inject_json_ld_schema")
        return _err("JSON-LD injection failed", str(e))


async def _suggest_internal_links(args: dict) -> list[TextContent]:
    try:
        result = _generator.suggest_internal_links(
            args["post_id"], args["wp_url"], args["username"], args["app_password"]
        )
        return _ok(result)
    except Exception as e:
        logger.exception("Error in suggest_internal_links")
        return _err("Internal link suggestion failed", str(e))


async def _apply_internal_links(args: dict) -> list[TextContent]:
    try:
        result = _generator.apply_internal_links(
            args["post_id"], args["wp_url"], args["username"], args["app_password"]
        )
        return _ok(result)
    except Exception as e:
        logger.exception("Error in apply_internal_links")
        return _err("Internal link application failed", str(e))


async def _generate_image_asset(args: dict) -> list[TextContent]:
    try:
        from app.image import ImageGenerator
        generator = ImageGenerator()
        result = generator.generate_image(
            prompt=args["prompt"],
            image_size=args.get("image_size", "landscape_4_3"),
        )
        return _ok({
            "success": True,
            "url": result.url,
            "prompt": result.prompt,
            "revised_prompt": result.revised_prompt,
            "width": result.width,
            "height": result.height,
            "created_at": result.created_at.isoformat(),
        })
    except Exception as e:
        logger.exception("Error in generate_image_asset")
        return _err("Image generation failed", str(e))


# ---------------------------------------------------------------------------
# Server entrypoint
# ---------------------------------------------------------------------------

async def main():
    """Run the MCP server using stdio transport."""
    logger.info("wp_ai_content MCP Server ready — listening on stdio")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
