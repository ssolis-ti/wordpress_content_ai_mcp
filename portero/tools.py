"""Portero tool wrappers for WordPress AI Content system.

This module provides @tool-decorated wrappers for each capability in the manifest.
Each tool imports from app.core and calls the real function with proper error handling.
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

# Import Portero tool decorator
try:
    from portero.decorators import tool
except ImportError:
    # Fallback for Portero compatibility
    from functools import wraps
    def tool(func=None, *, name=None, description=None):
        """Simple tool decorator for compatibility."""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
            wrapper.__tool_name__ = name or f.__name__
            wrapper.__tool_description__ = description or f.__doc__ or ""
            return wrapper
        if func is None:
            return decorator
        return decorator(func)

# Import app.core functionality
from app.core import get_content_generator, ContentGenerator, ImageGenerator
from app.models import BlogPost, SEOScore, SEOAuditResult, ResearchResult, WordPressPublishResult, GeneratedImage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize generators
_generator = get_content_generator()
_image_generator = ImageGenerator()


@tool(
    name="generate_blog_post",
    description="Generate full blog posts or pages from a topic, keywords, or outline. Creates SEO-optimized content with proper structure, headings, meta description, and image suggestions."
)
def generate_blog_post(
    topic: str,
    target_keywords: List[str],
    word_count: int = 1200,
    tone: str = "professional",
    target_audience: str = "general"
) -> Dict[str, Any]:
    """
    Generate a complete blog post with SEO optimization.
    
    Args:
        topic: Main topic of the blog post
        target_keywords: List of target keywords for SEO
        word_count: Desired word count (default 1200)
        tone: Content tone (professional, casual, authoritative, etc.)
        target_audience: Target audience description
        
    Returns:
        Dictionary with generated blog post data
        
    Example:
        generate_blog_post(
            topic="Artificial Intelligence in Marketing",
            target_keywords=["AI", "marketing automation", "personalization"],
            word_count=1500,
            tone="professional",
            target_audience="Marketing professionals"
        )
    """
    try:
        logger.info(f"Generating blog post: topic='{topic}', audience='{target_audience}'")
        
        # Call the actual implementation
        blog_post = _generator.generate_blog_post(
            topic=topic,
            target_keywords=target_keywords,
            word_count=word_count,
            tone=tone,
            target_audience=target_audience
        )
        
        # Convert to dictionary for serialization
        return {
            "success": True,
            "post_id": id(blog_post),  # Placeholder for actual ID
            "title": blog_post.metadata.title,
            "content": blog_post.content,
            "meta_description": blog_post.metadata.meta_description,
            "slug": blog_post.metadata.slug,
            "word_count": blog_post.word_count,
            "seo_score": {
                "overall": blog_post.seo_score.overall,
                "readability": blog_post.seo_score.readability,
                "keyword_density": blog_post.seo_score.keyword_density,
                "meta_optimization": blog_post.seo_score.meta_optimization,
                "technical_seo": blog_post.seo_score.technical_seo
            } if blog_post.seo_score else None,
            "seo_recommendations": [
                {
                    "category": rec.category,
                    "issue": rec.issue,
                    "suggestion": rec.suggestion,
                    "priority": rec.priority
                }
                for rec in blog_post.seo_recommendations
            ],
            "images_suggestions": blog_post.images_suggestions,
            "categories": blog_post.metadata.categories,
            "tags": blog_post.metadata.tags,
            "reading_time_minutes": blog_post.metadata.reading_time_minutes,
            "tone": blog_post.tone.value if hasattr(blog_post.tone, 'value') else str(blog_post.tone),
            "target_audience": blog_post.target_audience
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "error_type": "validation"
        }
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        return {
            "success": False,
            "error": f"Content generation failed: {str(e)}",
            "error_type": "runtime"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unexpected"
        }


@tool(
    name="seo_audit_and_optimize",
    description="Perform comprehensive SEO analysis on existing or generated content. Analyzes keyword usage, readability, structure, and provides optimization recommendations."
)
def seo_audit_and_optimize(
    content: str,
    primary_keyword: str,
    secondary_keywords: List[str]
) -> Dict[str, Any]:
    """
    Perform SEO audit and optimization on content.
    
    Args:
        content: Content to analyze and optimize
        primary_keyword: Primary keyword for SEO
        secondary_keywords: Secondary keywords for SEO
        
    Returns:
        Dictionary with SEO audit results and optimized content
        
    Example:
        seo_audit_and_optimize(
            content="# Digital Marketing\n\nContent about digital marketing...",
            primary_keyword="digital marketing",
            secondary_keywords=["SEO", "social media", "content marketing"]
        )
    """
    try:
        logger.info(f"Performing SEO audit for content with primary keyword: {primary_keyword}")
        
        # Call the actual implementation
        audit_result = _generator.seo_audit_and_optimize(
            content=content,
            primary_keyword=primary_keyword,
            secondary_keywords=secondary_keywords
        )
        
        # Convert to dictionary for serialization
        return {
            "success": True,
            "audit_id": id(audit_result),  # Placeholder for actual ID
            "seo_score": {
                "overall": audit_result.seo_score.overall,
                "readability": audit_result.seo_score.readability,
                "keyword_density": audit_result.seo_score.keyword_density,
                "meta_optimization": audit_result.seo_score.meta_optimization,
                "technical_seo": audit_result.seo_score.technical_seo
            },
            "recommendations": [
                {
                    "category": rec.category,
                    "issue": rec.issue,
                    "suggestion": rec.suggestion,
                    "priority": rec.priority
                }
                for rec in audit_result.recommendations
            ],
            "optimized_content": audit_result.optimized_content,
            "original_content": audit_result.original_content,
            "improvements_summary": audit_result.improvements_summary,
            "primary_keyword": audit_result.primary_keyword,
            "secondary_keywords": audit_result.secondary_keywords,
            "total_recommendations": len(audit_result.recommendations),
            "score_improvement": round(
                audit_result.seo_score.overall - 60.0, 1
            ),  # Baseline comparison (60 = average unoptimized content)
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "error_type": "validation"
        }
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        return {
            "success": False,
            "error": f"SEO audit failed: {str(e)}",
            "error_type": "runtime"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unexpected"
        }


@tool(
    name="research_topic",
    description="Conduct in-depth research on a topic including competitors, trends, and key facts. Provides comprehensive research findings for content planning."
)
def research_topic(
    topic: str,
    depth: str = "basic"
) -> Dict[str, Any]:
    """
    Research a topic for content creation.
    
    Args:
        topic: Topic to research
        depth: Research depth (basic, comprehensive)
        
    Returns:
        Dictionary with research findings
        
    Example:
        research_topic(
            topic="Content Marketing",
            depth="comprehensive"
        )
    """
    try:
        logger.info(f"Researching topic '{topic}' with depth: {depth}")
        
        # Call the actual implementation
        research_result = _generator.research_topic(
            topic=topic,
            depth=depth
        )
        
        # Convert to dictionary for serialization
        return {
            "success": True,
            "research_id": id(research_result),  # Placeholder for actual ID
            "topic": research_result.topic,
            "depth": research_result.depth,
            "key_findings": research_result.key_findings,
            "competitor_analysis": research_result.competitor_analysis,
            "trends": research_result.trends,
            "sources": research_result.sources,
            "recommendations": research_result.recommendations,
            "total_findings": len(research_result.key_findings),
            "total_competitors": len(research_result.competitor_analysis),
            "total_trends": len(research_result.trends)
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "error_type": "validation"
        }
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        return {
            "success": False,
            "error": f"Research failed: {str(e)}",
            "error_type": "runtime"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unexpected"
        }


@tool(
    name="publish_to_wordpress",
    description="Connect to WordPress instance and publish or update posts/pages. Requires WordPress credentials and content ready for publishing."
)
def publish_to_wordpress(
    content: Dict[str, Any],
    wp_url: str,
    username: str,
    app_password: str,
    status: str = "draft",
    categories: List[str] = None,
    tags: List[str] = None
) -> Dict[str, Any]:
    """
    Publish content to WordPress.
    
    Args:
        content: BlogPost content dictionary (from generate_blog_post)
        wp_url: WordPress site URL
        username: WordPress username
        app_password: WordPress application password
        status: Publication status (draft, publish)
        categories: Categories for WordPress post
        tags: Tags for WordPress post
        
    Returns:
        Dictionary with publishing results
        
    Example:
        publish_to_wordpress(
            content={...},  # BlogPost from generate_blog_post
            wp_url="https://example.com",
            username="admin",
            app_password="xxxx xxxx xxxx xxxx",
            status="publish",
            categories=["Marketing", "AI"],
            tags=["artificial intelligence", "automation"]
        )
    """
    try:
        logger.info(f"Publishing to WordPress: {content.get('title', 'Unknown title')}")
        
        # Convert content dictionary back to BlogPost object
        from app.models import BlogPost, ContentMetadata, ContentTone, SEOScore
        
        # Create metadata
        metadata = ContentMetadata(
            title=content.get('title', ''),
            meta_description=content.get('meta_description', ''),
            slug=content.get('slug', ''),
            reading_time_minutes=content.get('reading_time_minutes', 5),
            categories=content.get('categories', []),
            tags=content.get('tags', [])
        )
        
        # Create SEO score if available
        seo_score_data = content.get('seo_score')
        seo_score = None
        if seo_score_data:
            seo_score = SEOScore(
                overall=seo_score_data.get('overall', 0.0),
                readability=seo_score_data.get('readability', 0.0),
                keyword_density=seo_score_data.get('keyword_density', 0.0),
                meta_optimization=seo_score_data.get('meta_optimization', 0.0),
                technical_seo=seo_score_data.get('technical_seo', 0.0)
            )
        
        # Create BlogPost object
        blog_post = BlogPost(
            metadata=metadata,
            content=content.get('content', ''),
            tone=ContentTone(content.get('tone', 'professional')),
            target_audience=content.get('target_audience', 'general'),
            word_count=content.get('word_count', 0),
            target_keywords=content.get('target_keywords', []),
            seo_score=seo_score,
            seo_recommendations=[],  # Simplified for this example
            images_suggestions=content.get('images_suggestions', [])
        )
        
        # Call the actual implementation
        publish_result = _generator.publish_to_wordpress(
            content=blog_post,
            wp_url=wp_url,
            username=username,
            app_password=app_password,
            status=status,
            categories=categories,
            tags=tags
        )
        
        # Convert to dictionary for serialization
        return {
            "success": publish_result.success,
            "post_id": publish_result.post_id,
            "post_url": publish_result.post_url,
            "error_message": publish_result.error_message,
            "published_at": publish_result.published_at.isoformat() if publish_result.published_at else None,
            "title": content.get('title', ''),
            "status": status
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "error_type": "validation"
        }
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        return {
            "success": False,
            "error": f"WordPress publishing failed: {str(e)}",
            "error_type": "runtime"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unexpected"
        }


@tool(
    name="generate_image_asset",
    description="Generate high-quality image assets using fal.ai. Ideal for featured images, infographics descriptions, and post visuals."
)
def generate_image_asset(
    prompt: str,
    image_size: str = "landscape_4_3"
) -> Dict[str, Any]:
    """
    Generate an image based on a prompt.
    
    Args:
        prompt: Descriptive prompt for the image
        image_size: Dimensions of the image (square, landscape_4_3, etc.)
        
    Returns:
        Dictionary with image URL and metadata
    """
    try:
        logger.info(f"Generating image asset with prompt: {prompt}")
        
        # Call the actual implementation
        image_result = _image_generator.generate_image(
            prompt=prompt,
            image_size=image_size
        )
        
        return {
            "success": True,
            "url": image_result.url,
            "prompt": image_result.prompt,
            "revised_prompt": image_result.revised_prompt,
            "width": image_result.width,
            "height": image_result.height,
            "created_at": image_result.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in generate_image_asset: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "runtime"
        }


@tool(
    name="get_wordpress_posts",
    description="Retrieve existing posts from WordPress. Useful for reading content, auditing, or finding IDs of posts to update."
)
def get_wordpress_posts(
    wp_url: str,
    username: str,
    app_password: str,
    per_page: int = 10,
    page: int = 1
) -> Dict[str, Any]:
    """Retrieve posts from WordPress."""
    try:
        logger.info("Fetching WordPress posts")
        return _generator.get_wordpress_posts(wp_url, username, app_password, per_page, page)
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        return {"success": False, "error": str(e)}

@tool(
    name="update_wordpress_post",
    description="Update an existing WordPress post. Requires the post_id. You can update title, content (markdown), and status."
)
def update_wordpress_post(
    post_id: int,
    wp_url: str,
    username: str,
    app_password: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing WordPress post."""
    try:
        logger.info(f"Updating WordPress post ID: {post_id}")
        return _generator.update_wordpress_post(post_id, wp_url, username, app_password, title, content, status)
    except Exception as e:
        logger.error(f"Error updating post: {e}")
        return {"success": False, "error": str(e)}

@tool(
    name="create_wordpress_post",
    description="Create a simple WordPress post directly from text/markdown. Useful for quick manual posts without full SEO audit."
)
def create_wordpress_post(
    title: str,
    content: str,
    wp_url: str,
    username: str,
    app_password: str,
    status: str = "draft"
) -> Dict[str, Any]:
    """Create a simple WordPress post."""
    try:
        logger.info(f"Creating simple WordPress post: {title}")
        return _generator.create_simple_wordpress_post(title, content, wp_url, username, app_password, status)
    except Exception as e:
        logger.error(f"Error creating simple post: {e}")
        return {"success": False, "error": str(e)}


# Export all tools
__all__ = [
    'generate_blog_post',
    'seo_audit_and_optimize',
    'research_topic',
    'publish_to_wordpress',
    'generate_image_asset',
    'get_wordpress_posts',
    'update_wordpress_post',
    'create_wordpress_post'
]