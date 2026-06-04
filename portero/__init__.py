"""
Portero - AI Agent Orchestration Layer

This package defines the LLM agent, its tools, memory systems, and 
specialized behaviors for WordPress content generation workflows.
"""

from .agent import WpContentAgent, create_agent
from .tools import (
    generate_blog_post,
    seo_audit_and_optimize,
    research_topic,
    publish_to_wordpress,
    generate_image_asset
)

__version__ = "0.1.0"

__all__ = [
    "WpContentAgent",
    "create_agent",
    "generate_blog_post",
    "seo_audit_and_optimize",
    "research_topic",
    "publish_to_wordpress",
    "generate_image_asset"
]
