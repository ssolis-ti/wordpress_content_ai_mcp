"""Data models for WordPress AI Content system."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class ContentTone(str, Enum):
    """Available content tones."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    PERSUASIVE = "persuasive"


class ContentStatus(str, Enum):
    """Content status for WordPress."""
    DRAFT = "draft"
    PUBLISH = "publish"
    PENDING = "pending"
    PRIVATE = "private"


class SEOScore(BaseModel):
    """SEO scoring model."""
    overall: float = Field(..., ge=0, le=100, description="Overall SEO score (0-100)")
    readability: float = Field(..., ge=0, le=100, description="Readability score")
    keyword_density: float = Field(..., ge=0, le=100, description="Keyword optimization score")
    meta_optimization: float = Field(..., ge=0, le=100, description="Meta tags optimization score")
    technical_seo: float = Field(..., ge=0, le=100, description="Technical SEO score")


class SEORecommendation(BaseModel):
    """SEO recommendation item."""
    category: str = Field(..., description="Recommendation category")
    issue: str = Field(..., description="Description of the issue")
    suggestion: str = Field(..., description="Suggested improvement")
    priority: str = Field(..., description="Priority level (high, medium, low)")


class ContentMetadata(BaseModel):
    """Metadata for generated content."""
    title: str = Field(..., description="Content title")
    meta_description: str = Field(..., description="SEO meta description")
    slug: str = Field(..., description="URL slug")
    author: str = Field(default="AI Content Generator", description="Content author")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    featured_image: Optional[str] = Field(None, description="Featured image URL or path")
    categories: List[str] = Field(default_factory=list, description="Content categories")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    reading_time_minutes: int = Field(..., description="Estimated reading time in minutes")
    
    @validator('slug', pre=True, always=True)
    def validate_slug(cls, v, values):
        """Ensure slug is URL-friendly."""
        import re
        if not v:
            v = values.get('title', '')
        v = v.lower().strip()
        v = re.sub(r'[áàäâ]', 'a', v)
        v = re.sub(r'[éèëê]', 'e', v)
        v = re.sub(r'[íìïî]', 'i', v)
        v = re.sub(r'[óòöô]', 'o', v)
        v = re.sub(r'[úùüû]', 'u', v)
        v = re.sub(r'ñ', 'n', v)
        v = re.sub(r'[^\w\s-]', '', v)
        v = re.sub(r'[-\s]+', '-', v)
        return v


class BlogPost(BaseModel):
    """Complete blog post model."""
    metadata: ContentMetadata
    content: str = Field(..., description="Main content in markdown format")
    tone: ContentTone = Field(..., description="Content tone/style")
    target_audience: str = Field(..., description="Target audience description")
    word_count: int = Field(..., ge=1, description="Word count")
    target_keywords: List[str] = Field(default_factory=list, description="Target keywords for SEO")
    seo_score: Optional[SEOScore] = Field(None, description="SEO analysis score")
    seo_recommendations: List[SEORecommendation] = Field(default_factory=list, description="SEO recommendations")
    images_suggestions: List[str] = Field(default_factory=list, description="Suggested images")
    research_notes: Optional[str] = Field(None, description="Research notes and sources")
    
    @validator('word_count')
    def validate_word_count(cls, v):
        """Ensure word count is reasonable."""
        if v < 100:
            raise ValueError("Word count should be at least 100")
        if v > 10000:
            raise ValueError("Word count should not exceed 10,000")
        return v


class SEOAuditResult(BaseModel):
    """Results of SEO audit and optimization."""
    original_content: str = Field(..., description="Original content")
    optimized_content: str = Field(..., description="Optimized content")
    seo_score: SEOScore = Field(..., description="SEO scores")
    recommendations: List[SEORecommendation] = Field(..., description="SEO recommendations")
    primary_keyword: str = Field(..., description="Primary keyword used")
    secondary_keywords: List[str] = Field(default_factory=list, description="Secondary keywords")
    improvements_summary: str = Field(..., description="Summary of improvements made")


class ResearchResult(BaseModel):
    """Results of topic research."""
    topic: str = Field(..., description="Research topic")
    depth: str = Field(..., description="Research depth (basic, comprehensive)")
    key_findings: List[str] = Field(..., description="Key findings from research")
    competitor_analysis: List[Dict[str, Any]] = Field(default_factory=list, description="Competitor analysis")
    trends: List[str] = Field(default_factory=list, description="Current trends")
    sources: List[str] = Field(default_factory=list, description="Research sources")
    recommendations: List[str] = Field(default_factory=list, description="Content recommendations")


class WordPressPublishRequest(BaseModel):
    """Request for publishing to WordPress."""
    content: BlogPost = Field(..., description="Content to publish")
    wp_url: str = Field(..., description="WordPress site URL")
    username: str = Field(..., description="WordPress username")
    app_password: str = Field(..., description="WordPress application password")
    status: ContentStatus = Field(default=ContentStatus.DRAFT, description="Publication status")
    categories: List[str] = Field(default_factory=list, description="Categories for WordPress")
    tags: List[str] = Field(default_factory=list, description="Tags for WordPress")
    
    @validator('wp_url')
    def validate_wp_url(cls, v):
        """Validate WordPress URL format."""
        import re
        if not re.match(r'^https?://', v):
            v = f'https://{v}'
        return v.rstrip('/')


class WordPressPublishResult(BaseModel):
    """Result of WordPress publishing."""
    success: bool = Field(..., description="Whether publishing was successful")
    post_id: Optional[int] = Field(None, description="WordPress post ID")
    post_url: Optional[str] = Field(None, description="Published post URL")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    
    
class GeneratedImage(BaseModel):
    """Model for generated image asset."""
    prompt: str = Field(..., description="Original prompt used for generation")
    revised_prompt: Optional[str] = Field(None, description="Revised prompt by the AI")
    url: str = Field(..., description="Image URL")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    local_path: Optional[str] = Field(None, description="Local path if downloaded")