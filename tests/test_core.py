"""Tests for WordPress AI Content core functionality."""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path to access the app module
sys.path.insert(0, str(Path(__file__).parent.parent))

import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.core import ContentGenerator, get_content_generator
from app.models import (
    BlogPost, ContentMetadata, ContentTone, SEOScore, SEORecommendation,
    SEOAuditResult, ResearchResult, WordPressPublishResult, ContentStatus
)
from app.storage import StorageManager


class TestContentGenerator(unittest.TestCase):
    """Test cases for ContentGenerator class."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset storage and core singletons to avoid path bleed between test runs
        import app.storage
        import app.core
        app.storage._storage_manager = None
        app.core._content_generator = None

        # Create temporary directory for test data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name)
        
        # Initialize content generator with test data path
        self.generator = ContentGenerator(self.data_path)
        
        # Sample data for tests
        self.sample_topic = "Artificial Intelligence in Business"
        self.sample_keywords = ["AI", "automation", "machine learning", "productivity"]
        self.sample_content = """
        # Artificial Intelligence in Business
        
        Artificial Intelligence is transforming how businesses operate.
        
        ## Benefits of AI
        
        AI can automate repetitive tasks and provide insights.
        
        ## Implementation Strategies
        
        Start with small pilot projects and scale gradually.
        """

        # Define mock LLM responses based on prompt
        def mock_call_llm(prompt, max_tokens=4000):
            import re
            prompt_lower = prompt.lower()
            topic = self.sample_topic
            topic_match = re.search(r'sobre "([^"]+)"', prompt) or re.search(r'sobre\s+([^.\n]+)', prompt)
            if topic_match:
                topic = topic_match.group(1).strip()
            elif "investigar sobre" in prompt_lower:
                match = re.search(r'investigar sobre "([^"]+)"', prompt) or re.search(r'investigar sobre\s+([^.\n]+)', prompt)
                if match:
                    topic = match.group(1).strip()
            elif "artículo sobre" in prompt_lower:
                match = re.search(r'artículo sobre "([^"]+)"', prompt) or re.search(r'artículo sobre\s+([^.\n]+)', prompt)
                if match:
                    topic = match.group(1).strip()
            
            topic = topic.strip('"').strip("'")

            if "json" in prompt_lower or "competitor" in prompt_lower or "panorama" in prompt_lower:
                return '[{"competitor": "Tech Blogs", "strength": "Detailed guides", "weakness": "Slow updates"}, {"competitor": "News sites", "strength": "Fast coverage", "weakness": "Shallow content"}]'
            elif "meta" in prompt_lower:
                return f"{topic} is transforming modern enterprise productivity. Explore the latest automation strategies."[:160]
            elif "lista" in prompt_lower or "hallazgos" in prompt_lower or "tendencias" in prompt_lower or "fuentes" in prompt_lower or "recomendaciones" in prompt_lower:
                return "\n".join(f"{i}. Mocked finding/trend/source item {i} about {topic}" for i in range(1, 10))
            else:
                return f"# {topic}\n\n{topic} is transforming business operations and automation. We see significant adoption.\n\n## Benefits\n\nIt increases productivity.\n\n## Future Trends\n\nAutomation is the future."

        # Start patchers for all call_llm imports to mock actual LLM API calls during tests
        self.patchers = [
            patch('app.generator.call_llm', side_effect=mock_call_llm),
            patch('app.seo.call_llm', side_effect=mock_call_llm),
            patch('app.research.call_llm', side_effect=mock_call_llm)
        ]
        for p in self.patchers:
            p.start()
    
    def tearDown(self):
        """Clean up test environment."""
        for p in self.patchers:
            p.stop()
        self.temp_dir.cleanup()
    
    def test_generate_blog_post_valid(self):
        """Test generating a blog post with valid parameters."""
        # Act
        blog_post = self.generator.generate_blog_post(
            topic=self.sample_topic,
            target_keywords=self.sample_keywords,
            word_count=800,
            tone="professional",
            target_audience="Business executives"
        )
        
        # Assert
        self.assertIsInstance(blog_post, BlogPost)
        self.assertEqual(blog_post.metadata.title, self.sample_topic)
        self.assertEqual(blog_post.tone, ContentTone.PROFESSIONAL)
        self.assertEqual(blog_post.target_audience, "Business executives")
        self.assertEqual(blog_post.word_count, 800)
        self.assertEqual(blog_post.target_keywords, self.sample_keywords)
        self.assertIsInstance(blog_post.seo_score, SEOScore)
        self.assertGreater(len(blog_post.content), 0)
        self.assertGreater(len(blog_post.metadata.meta_description), 0)
        self.assertGreater(len(blog_post.metadata.slug), 0)
    
    def test_generate_blog_post_invalid_topic(self):
        """Test generating a blog post with empty topic."""
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.generate_blog_post(
                topic="",
                target_keywords=self.sample_keywords,
                word_count=800,
                tone="professional",
                target_audience="Business executives"
            )
    
    def test_generate_blog_post_invalid_word_count(self):
        """Test generating a blog post with invalid word count."""
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.generate_blog_post(
                topic=self.sample_topic,
                target_keywords=self.sample_keywords,
                word_count=50,  # Too low
                tone="professional",
                target_audience="Business executives"
            )
    
    def test_generate_blog_post_invalid_tone(self):
        """Test generating a blog post with invalid tone."""
        # Act
        # Should default to professional tone
        blog_post = self.generator.generate_blog_post(
            topic=self.sample_topic,
            target_keywords=self.sample_keywords,
            word_count=800,
            tone="invalid_tone",  # Invalid tone
            target_audience="Business executives"
        )
        
        # Assert - should default to professional
        self.assertEqual(blog_post.tone, ContentTone.PROFESSIONAL)
    
    def test_seo_audit_and_optimize_valid(self):
        """Test performing SEO audit with valid content."""
        # Act
        audit_result = self.generator.seo_audit_and_optimize(
            content=self.sample_content,
            primary_keyword="artificial intelligence",
            secondary_keywords=["business", "automation", "AI"]
        )
        
        # Assert
        self.assertIsInstance(audit_result, SEOAuditResult)
        self.assertEqual(audit_result.original_content, self.sample_content)
        self.assertIsInstance(audit_result.optimized_content, str)
        self.assertGreater(len(audit_result.optimized_content), 0)
        self.assertIsInstance(audit_result.seo_score, SEOScore)
        self.assertIsInstance(audit_result.recommendations, list)
        self.assertEqual(audit_result.primary_keyword, "artificial intelligence")
        self.assertEqual(audit_result.secondary_keywords, ["business", "automation", "AI"])
        self.assertGreater(len(audit_result.improvements_summary), 0)
        
        # Verify SEO score ranges
        self.assertGreaterEqual(audit_result.seo_score.overall, 0)
        self.assertLessEqual(audit_result.seo_score.overall, 100)
    
    def test_seo_audit_and_optimize_empty_content(self):
        """Test performing SEO audit with empty content."""
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.seo_audit_and_optimize(
                content="",
                primary_keyword="test",
                secondary_keywords=[]
            )
    
    def test_seo_audit_and_optimize_empty_keyword(self):
        """Test performing SEO audit with empty primary keyword."""
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.seo_audit_and_optimize(
                content=self.sample_content,
                primary_keyword="",
                secondary_keywords=[]
            )
    
    def test_research_topic_valid(self):
        """Test researching a topic with valid parameters."""
        # Act
        research_result = self.generator.research_topic(
            topic="Digital Marketing",
            depth="basic"
        )
        
        # Assert
        self.assertIsInstance(research_result, ResearchResult)
        self.assertEqual(research_result.topic, "Digital Marketing")
        self.assertEqual(research_result.depth, "basic")
        self.assertIsInstance(research_result.key_findings, list)
        self.assertGreater(len(research_result.key_findings), 0)
        self.assertIsInstance(research_result.competitor_analysis, list)
        self.assertIsInstance(research_result.trends, list)
        self.assertIsInstance(research_result.sources, list)
        self.assertIsInstance(research_result.recommendations, list)
    
    def test_research_topic_comprehensive(self):
        """Test comprehensive research on a topic."""
        # Act
        research_result = self.generator.research_topic(
            topic="Content Marketing",
            depth="comprehensive"
        )
        
        # Assert
        self.assertEqual(research_result.depth, "comprehensive")
        # Comprehensive research should have more findings than basic
        self.assertGreater(len(research_result.key_findings), 3)
    
    def test_research_topic_invalid_topic(self):
        """Test researching with empty topic."""
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.research_topic(topic="", depth="basic")
    
    def test_research_topic_invalid_depth(self):
        """Test researching with invalid depth."""
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.research_topic(topic="Marketing", depth="invalid")
    
    @patch('app.publisher.WordPressPublisher.publish')
    def test_publish_to_wordpress_valid(self, mock_publish):
        """Test publishing to WordPress with valid parameters."""
        # Arrange
        mock_publish.return_value = WordPressPublishResult(
            success=True,
            post_id=1234,
            post_url="https://example.com/test-post",
            published_at=datetime.now()
        )
        
        # Create a test blog post
        metadata = ContentMetadata(
            title="Test Post",
            meta_description="Test description",
            slug="test-post",
            reading_time_minutes=5
        )
        
        test_post = BlogPost(
            metadata=metadata,
            content="# Test Content\n\nThis is a test.",
            tone="professional",
            target_audience="Testers",
            word_count=100,
            target_keywords=["test"]
        )
        
        # Act
        publish_result = self.generator.publish_to_wordpress(
            content=test_post,
            wp_url="https://example.com",
            username="admin",
            app_password="test123",
            status="draft"
        )
        
        # Assert
        self.assertIsInstance(publish_result, WordPressPublishResult)
        self.assertTrue(publish_result.success)
        self.assertEqual(publish_result.post_id, 1234)
        self.assertEqual(publish_result.post_url, "https://example.com/test-post")
        self.assertIsNone(publish_result.error_message)
        self.assertIsNotNone(publish_result.published_at)
    
    def test_publish_to_wordpress_invalid_url(self):
        """Test publishing to WordPress with empty URL."""
        # Arrange
        metadata = ContentMetadata(
            title="Test Post",
            meta_description="Test description",
            slug="test-post",
            reading_time_minutes=5
        )
        
        test_post = BlogPost(
            metadata=metadata,
            content="# Test Content",
            tone="professional",
            target_audience="Testers",
            word_count=100,
            target_keywords=["test"]
        )
        
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.publish_to_wordpress(
                content=test_post,
                wp_url="",
                username="admin",
                app_password="test123",
                status="draft"
            )
    
    def test_publish_to_wordpress_invalid_status(self):
        """Test publishing to WordPress with invalid status."""
        # Arrange
        metadata = ContentMetadata(
            title="Test Post",
            meta_description="Test description",
            slug="test-post",
            reading_time_minutes=5
        )
        
        test_post = BlogPost(
            metadata=metadata,
            content="# Test Content",
            tone="professional",
            target_audience="Testers",
            word_count=100,
            target_keywords=["test"]
        )
        
        # Act & Assert
        with self.assertRaises(ValueError):
            self.generator.publish_to_wordpress(
                content=test_post,
                wp_url="https://example.com",
                username="admin",
                app_password="test123",
                status="invalid_status"
            )
    
    def test_generate_slug(self):
        """Test slug generation."""
        # Act
        slug1 = self.generator._generate_slug("Test Blog Post")
        slug2 = self.generator._generate_slug("AI & Machine Learning: 2024 Trends!")
        slug3 = self.generator._generate_slug("")  # Empty should generate timestamp-based slug
        
        # Assert
        self.assertEqual(slug1, "test-blog-post")
        self.assertEqual(slug2, "ai-machine-learning-2024-trends")
        self.assertIn("post-", slug3)  # Should start with "post-"
    
    def test_generate_meta_description(self):
        """Test meta description generation."""
        # Act
        meta_desc = self.generator._generate_meta_description(
            "Digital Marketing",
            ["SEO", "social media", "content marketing"]
        )
        
        # Assert
        self.assertIsInstance(meta_desc, str)
        self.assertGreater(len(meta_desc), 0)
        self.assertLessEqual(len(meta_desc), 160)  # Should be SEO-friendly length
        self.assertIn("Digital Marketing", meta_desc)
    
    def test_calculate_seo_score(self):
        """Test SEO score calculation."""
        # Act
        seo_score = self.generator._calculate_seo_score(
            self.sample_content,
            self.sample_keywords
        )
        
        # Assert
        self.assertIsInstance(seo_score, SEOScore)
        self.assertGreaterEqual(seo_score.overall, 0)
        self.assertLessEqual(seo_score.overall, 100)
        self.assertGreaterEqual(seo_score.readability, 0)
        self.assertLessEqual(seo_score.readability, 100)
        self.assertGreaterEqual(seo_score.keyword_density, 0)
        self.assertLessEqual(seo_score.keyword_density, 100)
    
    def test_generate_seo_recommendations(self):
        """Test SEO recommendations generation."""
        # Arrange
        seo_score = SEOScore(
            overall=75.0,
            readability=80.0,
            keyword_density=50.0,  # Low density
            meta_optimization=85.0,
            technical_seo=80.0
        )
        
        # Act
        recommendations = self.generator._generate_seo_recommendations(
            self.sample_content,
            self.sample_keywords,
            seo_score
        )
        
        # Assert
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Check that at least one recommendation is about keyword density
        keyword_recommendations = [
            r for r in recommendations 
            if "keyword" in r.category.lower() or "keyword" in r.issue.lower()
        ]
        self.assertGreater(len(keyword_recommendations), 0)
    
    def test_optimize_content(self):
        """Test content optimization."""
        # Arrange
        recommendations = [
            SEORecommendation(
                category="Keywords",
                issue="Low keyword density",
                suggestion="Add more primary keywords",
                priority="medium"
            ),
            SEORecommendation(
                category="Structure",
                issue="Missing H1 heading",
                suggestion="Add H1 heading",
                priority="high"
            )
        ]
        
        # Act
        optimized = self.generator._optimize_content(
            self.sample_content,
            "artificial intelligence",
            ["AI", "machine learning"],
            recommendations
        )
        
        # Assert
        self.assertIsInstance(optimized, str)
        self.assertGreater(len(optimized), len(self.sample_content))
        self.assertIn("artificial intelligence", optimized.lower())
    
    def test_get_content_generator_singleton(self):
        """Test that get_content_generator returns singleton instance."""
        # Act
        generator1 = get_content_generator(self.data_path)
        generator2 = get_content_generator(self.data_path)
        
        # Assert
        self.assertIs(generator1, generator2)
        self.assertIsInstance(generator1, ContentGenerator)
    
    def test_storage_integration(self):
        """Test that generated content is stored in database."""
        # Act
        blog_post = self.generator.generate_blog_post(
            topic="Test Storage Integration",
            target_keywords=["test", "storage"],
            word_count=500,
            tone="professional",
            target_audience="Developers"
        )
        
        # Get storage manager
        storage = self.generator.storage
        
        # Assert - should have at least one blog post in storage
        all_posts = storage.blog_posts.get_all()
        self.assertGreater(len(all_posts), 0)
        
        # Find our test post
        test_post = None
        for post in all_posts:
            if post.metadata.title == "Test Storage Integration":
                test_post = post
                break
        
        self.assertIsNotNone(test_post)
        self.assertEqual(test_post.metadata.title, "Test Storage Integration")


class TestModels(unittest.TestCase):
    """Test cases for data models."""
    
    def test_blog_post_validation(self):
        """Test BlogPost model validation."""
        # Valid blog post
        metadata = ContentMetadata(
            title="Test Post",
            meta_description="Test description",
            slug="test-post",
            reading_time_minutes=5
        )
        
        blog_post = BlogPost(
            metadata=metadata,
            content="# Test Content",
            tone="professional",
            target_audience="Testers",
            word_count=500,  # Valid word count
            target_keywords=["test"]
        )
        
        self.assertIsInstance(blog_post, BlogPost)
        self.assertEqual(blog_post.word_count, 500)
    
    def test_blog_post_invalid_word_count(self):
        """Test BlogPost model with invalid word count."""
        metadata = ContentMetadata(
            title="Test Post",
            meta_description="Test description",
            slug="test-post",
            reading_time_minutes=5
        )
        
        # Should raise ValueError for word count < 100
        with self.assertRaises(ValueError):
            BlogPost(
                metadata=metadata,
                content="# Test Content",
                tone="professional",
                target_audience="Testers",
                word_count=50,  # Invalid: too low
                target_keywords=["test"]
            )
    
    def test_content_metadata_slug_validation(self):
        """Test ContentMetadata slug validation."""
        # Test slug generation from title with special characters
        metadata = ContentMetadata(
            title="AI & ML: Best Practices 2024!",
            meta_description="Test",
            slug="",  # Will be validated
            reading_time_minutes=5
        )
        
        # Slug should be cleaned
        self.assertEqual(metadata.slug, "ai-ml-best-practices-2024")
    
    def test_seo_score_validation(self):
        """Test SEOScore model validation."""
        # Valid scores
        seo_score = SEOScore(
            overall=85.5,
            readability=90.0,
            keyword_density=80.0,
            meta_optimization=85.0,
            technical_seo=87.0
        )
        
        self.assertIsInstance(seo_score, SEOScore)
        self.assertEqual(seo_score.overall, 85.5)
        
        # Invalid score (should be clamped by Pydantic)
        with self.assertRaises(ValueError):
            SEOScore(
                overall=150.0,  # Invalid: > 100
                readability=90.0,
                keyword_density=80.0,
                meta_optimization=85.0,
                technical_seo=87.0
            )


if __name__ == "__main__":
    unittest.main()