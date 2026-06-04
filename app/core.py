"""Core Facade interface for WordPress AI Content system."""

import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.storage import get_storage_manager
from app.models import (
    BlogPost, ContentMetadata, ContentTone, SEOScore, SEORecommendation,
    SEOAuditResult, ResearchResult, WordPressPublishRequest,
    WordPressPublishResult, ContentStatus, GeneratedImage
)

# Import sub-modules for clean architectural delegation
from app.generator import ContentGeneratorEngine
from app.seo import SEOAuditor
from app.research import TopicResearcher
from app.publisher import WordPressPublisher
from app.image import ImageGenerator

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Facade core content generation engine."""
    
    def __init__(self, storage_path: Path = Path("data")):
        """Initialize content generator."""
        self.storage = get_storage_manager(storage_path)
        self.default_word_count = 1500
        self.engine = ContentGeneratorEngine()
        self.seo_auditor = SEOAuditor()
        self.researcher = TopicResearcher()
        self.publisher = WordPressPublisher()
        
    def generate_blog_post(
        self,
        topic: str,
        target_keywords: List[str] = None,
        word_count: int = 1200,
        tone: str = "professional",
        target_audience: str = "general"
    ) -> BlogPost:
        post = self.engine.generate_blog_post(topic, target_keywords, word_count, tone, target_audience)
        self.storage.blog_posts.create(post)
        return post

    # Backward compatibility delegate methods for testing
    def _generate_slug(self, topic: str) -> str:
        return self.engine._generate_slug(topic)

    def _generate_meta_description(self, topic: str, keywords: List[str], content: str = "") -> str:
        return self.engine._generate_meta_description(topic, keywords, content)

    def _calculate_seo_score(self, content: str, keywords: List[str]) -> SEOScore:
        primary = keywords[0] if keywords else ""
        secondary = keywords[1:] if len(keywords) > 1 else []
        return self.seo_auditor._calculate_seo_score(content, primary, secondary)

    def _generate_seo_recommendations(self, content: str, keywords: List[str], seo_score: SEOScore) -> List[SEORecommendation]:
        primary = keywords[0] if keywords else ""
        secondary = keywords[1:] if len(keywords) > 1 else []
        return self.seo_auditor._generate_recommendations(content, primary, secondary, seo_score)

    def _optimize_content(self, content: str, primary_keyword: str, secondary_keywords: List[str], recommendations: List[SEORecommendation]) -> str:
        return self.seo_auditor._optimize_content(content, primary_keyword, secondary_keywords, recommendations)

    def seo_audit_and_optimize(
        self,
        content: str,
        primary_keyword: str,
        secondary_keywords: List[str] = None
    ) -> SEOAuditResult:
        return self.seo_auditor.audit_content(content, primary_keyword, secondary_keywords)

    def audit_seo_entities(self, post_content: str, topic: str) -> Dict[str, Any]:
        return self.seo_auditor.audit_seo_entities(post_content, topic)

    def research_topic(self, topic: str, depth: str = "basic") -> ResearchResult:
        return self.researcher.research(topic, depth)

    def publish_to_wordpress(
        self,
        content: BlogPost,
        wp_url: str,
        username: str,
        app_password: str,
        status: str = "draft",
        categories: List[str] = None,
        tags: List[str] = None
    ) -> WordPressPublishResult:
        result = self.publisher.publish(content, wp_url, username, app_password, status, categories, tags)
        # Store result in local database to keep history synchronized
        if result.success:
            self.storage.publish_results.create(result)
        return result

    def get_wordpress_categories(self, wp_url: str, username: str, app_password: str) -> Dict[str, Any]:
        return self.publisher.get_wordpress_categories(wp_url, username, app_password)

    def update_wordpress_post(
        self,
        post_id: int,
        wp_url: str,
        username: str,
        app_password: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None,
        slug: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        return self.publisher.update_wordpress_post(post_id, wp_url, username, app_password, title, content, status, slug, categories)

    def inject_json_ld_schema(self, post_id: int, wp_url: str, username: str, app_password: str) -> Dict[str, Any]:
        return self.publisher.inject_json_ld_schema(post_id, wp_url, username, app_password)

    def suggest_internal_links(self, post_id: int, wp_url: str, username: str, app_password: str) -> Dict[str, Any]:
        return self.publisher.suggest_internal_links(post_id, wp_url, username, app_password)

    def apply_internal_links(self, post_id: int, wp_url: str, username: str, app_password: str) -> Dict[str, Any]:
        return self.publisher.apply_internal_links(post_id, wp_url, username, app_password)

    def get_wordpress_posts(
        self,
        wp_url: str,
        username: str,
        app_password: str,
        per_page: int = 10,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Retrieve a paginated list of posts from WordPress."""
        return self.publisher.get_wordpress_posts(wp_url, username, app_password, per_page, page)

    def create_simple_wordpress_post(
        self,
        title: str,
        content: str,
        wp_url: str,
        username: str,
        app_password: str,
        status: str = "draft",
    ) -> Dict[str, Any]:
        """Create a simple WordPress post from plain markdown (no BlogPost object needed)."""
        return self.publisher.create_simple_post(title, content, wp_url, username, app_password, status)


# =====================================================================
# BACKWARDS COMPATIBILITY WRAPPERS FOR MCP SERVER & EXTERNAL CLIENTS
# =====================================================================

# Exporting these classes with original names to prevent import crashes
# and keep the codebase decoupled and clean.

_content_generator: Optional[ContentGenerator] = None

def get_content_generator(storage_path: Path = Path("data")) -> ContentGenerator:
    """Get or create global content generator instance."""
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGenerator(storage_path)
    return _content_generator

