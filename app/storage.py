"""JSON storage backend for WordPress AI Content system."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from typing_extensions import Self
import logging

from app.models import (
    BlogPost, SEOAuditResult, ResearchResult, 
    WordPressPublishResult, ContentMetadata
)

T = TypeVar('T')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JSONStorage(Generic[T]):
    """Generic JSON storage class for different data types."""
    
    def __init__(self, storage_path: Path, data_type: Type[T]):
        """
        Initialize JSON storage.
        
        Args:
            storage_path: Path to storage directory
            data_type: Type of data to store (Pydantic model class)
        """
        self.storage_path = storage_path
        self.data_type = data_type
        self.data_file = storage_path / f"{data_type.__name__.lower()}.json"
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize data
        self._data: Dict[str, Dict[str, Any]] = self._load_data()
    
    def _load_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load data from JSON file.
        
        Returns:
            Dictionary of loaded data
        """
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} items from {self.data_file}")
                    return data
            else:
                logger.info(f"Creating new storage file: {self.data_file}")
                return {}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading data from {self.data_file}: {e}")
            return {}
    
    def _save_data(self) -> bool:
        """
        Save data to JSON file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, default=self._json_serializer)
            logger.info(f"Saved {len(self._data)} items to {self.data_file}")
            return True
        except (IOError, TypeError) as e:
            logger.error(f"Error saving data to {self.data_file}: {e}")
            return False
    
    def _json_serializer(self, obj):
        """
        Custom JSON serializer for datetime and other non-serializable objects.
        
        Args:
            obj: Object to serialize
            
        Returns:
            JSON-serializable representation
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def create(self, item: T) -> str:
        """
        Create a new item with generated ID.
        
        Args:
            item: Item to store
            
        Returns:
            Generated ID for the item
        """
        try:
            # Generate unique ID
            item_id = str(uuid.uuid4())
            
            # Convert to dictionary
            item_dict = item.model_dump(mode='json')

            item_dict['_id'] = item_id
            item_dict['_created_at'] = datetime.now().isoformat()
            item_dict['_updated_at'] = datetime.now().isoformat()
            
            # Store in memory
            self._data[item_id] = item_dict
            
            # Save to disk
            if self._save_data():
                logger.info(f"Created {self.data_type.__name__} with ID: {item_id}")
                return item_id
            else:
                logger.error(f"Failed to save {self.data_type.__name__} with ID: {item_id}")
                raise RuntimeError("Failed to save data to storage")
                
        except Exception as e:
            logger.error(f"Error creating {self.data_type.__name__}: {e}")
            raise
    
    def get(self, item_id: str) -> Optional[T]:
        """
        Get item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            Item if found, None otherwise
        """
        try:
            if item_id in self._data:
                item_dict = self._data[item_id]
                # Remove internal metadata before parsing
                clean_dict = {k: v for k, v in item_dict.items() if not k.startswith('_')}
                return self.data_type(**clean_dict)
            return None
        except Exception as e:
            logger.error(f"Error getting {self.data_type.__name__} {item_id}: {e}")
            return None
    
    def get_all(self) -> List[T]:
        """
        Get all items.
        
        Returns:
            List of all items
        """
        try:
            items = []
            for item_id, item_dict in self._data.items():
                # Remove internal metadata before parsing
                clean_dict = {k: v for k, v in item_dict.items() if not k.startswith('_')}
                items.append(self.data_type(**clean_dict))
            return items
        except Exception as e:
            logger.error(f"Error getting all {self.data_type.__name__}: {e}")
            return []
    
    def update(self, item_id: str, item: T) -> bool:
        """
        Update existing item.
        
        Args:
            item_id: Item ID
            item: Updated item
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if item_id not in self._data:
                logger.warning(f"{self.data_type.__name__} {item_id} not found for update")
                return False
            
            # Convert to dictionary
            item_dict = item.model_dump(mode='json')

            item_dict['_id'] = item_id
            item_dict['_created_at'] = self._data[item_id]['_created_at']
            item_dict['_updated_at'] = datetime.now().isoformat()
            
            # Update in memory
            self._data[item_id] = item_dict
            
            # Save to disk
            if self._save_data():
                logger.info(f"Updated {self.data_type.__name__} with ID: {item_id}")
                return True
            else:
                logger.error(f"Failed to save updated {self.data_type.__name__} with ID: {item_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating {self.data_type.__name__} {item_id}: {e}")
            return False
    
    def delete(self, item_id: str) -> bool:
        """
        Delete item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if item_id in self._data:
                del self._data[item_id]
                if self._save_data():
                    logger.info(f"Deleted {self.data_type.__name__} with ID: {item_id}")
                    return True
                else:
                    logger.error(f"Failed to save after deleting {self.data_type.__name__} {item_id}")
                    return False
            else:
                logger.warning(f"{self.data_type.__name__} {item_id} not found for deletion")
                return False
        except Exception as e:
            logger.error(f"Error deleting {self.data_type.__name__} {item_id}: {e}")
            return False
    
    def search(self, **kwargs) -> List[T]:
        """
        Search items by field values.
        
        Args:
            **kwargs: Field name and value pairs to search for
            
        Returns:
            List of matching items
        """
        try:
            results = []
            for item_id, item_dict in self._data.items():
                # Remove internal metadata
                clean_dict = {k: v for k, v in item_dict.items() if not k.startswith('_')}
                
                # Check if all search criteria match
                match = True
                for field, value in kwargs.items():
                    if field not in clean_dict or clean_dict[field] != value:
                        match = False
                        break
                
                if match:
                    results.append(self.data_type(**clean_dict))
            
            return results
        except Exception as e:
            logger.error(f"Error searching {self.data_type.__name__}: {e}")
            return []
    
    def count(self) -> int:
        """
        Get total number of items.
        
        Returns:
            Number of items
        """
        return len(self._data)
    
    def clear(self) -> bool:
        """
        Clear all items.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._data.clear()
            return self._save_data()
        except Exception as e:
            logger.error(f"Error clearing {self.data_type.__name__} storage: {e}")
            return False


class StorageManager:
    """Main storage manager for the application."""
    
    def __init__(self, data_path: Path = Path("data")):
        """
        Initialize storage manager.
        
        Args:
            data_path: Path to data directory
        """
        self.data_path = data_path
        
        # Initialize storage for each data type
        self.blog_posts = JSONStorage[BlogPost](self.data_path, BlogPost)
        self.seo_audits = JSONStorage[SEOAuditResult](self.data_path, SEOAuditResult)
        self.research_results = JSONStorage[ResearchResult](self.data_path, ResearchResult)
        self.publish_results = JSONStorage[WordPressPublishResult](self.data_path, WordPressPublishResult)
    
    def get_blog_post_by_title(self, title: str) -> Optional[BlogPost]:
        """
        Get blog post by title.
        
        Args:
            title: Blog post title
            
        Returns:
            BlogPost if found, None otherwise
        """
        try:
            posts = self.blog_posts.search()
            for post in posts:
                if post.metadata.title.lower() == title.lower():
                    return post
            return None
        except Exception as e:
            logger.error(f"Error searching blog post by title '{title}': {e}")
            return None
    
    def get_blog_posts_by_keyword(self, keyword: str) -> List[BlogPost]:
        """
        Get blog posts containing specific keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching blog posts
        """
        try:
            posts = self.blog_posts.search()
            results = []
            for post in posts:
                if (keyword.lower() in post.metadata.title.lower() or 
                    keyword.lower() in post.content.lower() or
                    keyword.lower() in ' '.join(post.target_keywords).lower()):
                    results.append(post)
            return results
        except Exception as e:
            logger.error(f"Error searching blog posts by keyword '{keyword}': {e}")
            return []
    
    def get_recent_blog_posts(self, limit: int = 10) -> List[BlogPost]:
        """
        Get most recent blog posts.
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            List of recent blog posts
        """
        try:
            posts = self.blog_posts.get_all()
            # Sort by creation date (newest first)
            posts.sort(key=lambda x: x.metadata.created_at, reverse=True)
            return posts[:limit]
        except Exception as e:
            logger.error(f"Error getting recent blog posts: {e}")
            return []
    
    def get_seo_audits_for_post(self, post_id: str) -> List[SEOAuditResult]:
        """
        Get SEO audits for a specific blog post.
        
        Args:
            post_id: Blog post ID
            
        Returns:
            List of SEO audits for the post
        """
        try:
            # This would require storing post_id reference in SEOAuditResult
            # For now, return all audits
            return self.seo_audits.get_all()
        except Exception as e:
            logger.error(f"Error getting SEO audits for post {post_id}: {e}")
            return []
    
    def backup(self, backup_path: Optional[Path] = None) -> bool:
        """
        Create backup of all data.
        
        Args:
            backup_path: Path for backup directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if backup_path is None:
                backup_path = self.data_path / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copy all JSON files
            for json_file in self.data_path.glob("*.json"):
                backup_file = backup_path / json_file.name
                import shutil
                shutil.copy2(json_file, backup_file)
            
            logger.info(f"Created backup at: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False


# Global storage instance
_storage_manager: Optional[StorageManager] = None


def get_storage_manager(data_path: Path = Path("data")) -> StorageManager:
    """
    Get or create global storage manager instance.
    
    Args:
        data_path: Path to data directory
        
    Returns:
        StorageManager instance
    """
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager(data_path)
    return _storage_manager


if __name__ == "__main__":
    """Test the storage system."""
    import tempfile
    from datetime import datetime
    
    # Create temporary directory for testing
    # Use a persistent test directory instead of tempfile
    tmp_path = Path("data/test")
    tmp_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize storage
    storage = StorageManager(tmp_path)
    
    # Test BlogPost storage
    print("Testing BlogPost storage...")
    
    # Create a sample blog post
    metadata = ContentMetadata(
        title="Test Blog Post",
        meta_description="This is a test blog post",
        slug="test-blog-post",
        reading_time_minutes=5
    )
    
    blog_post = BlogPost(
        metadata=metadata,
        content="# Test Content\n\nThis is test content.",
        tone="professional",
        target_audience="Developers",
        word_count=100,
        target_keywords=["test", "blog", "content"]
    )
    
    # Create
    post_id = storage.blog_posts.create(blog_post)
    print(f"Created blog post with ID: {post_id}")
    
    # Get
    retrieved_post = storage.blog_posts.get(post_id)
    print(f"Retrieved blog post title: {retrieved_post.metadata.title}")
    
    # Update
    retrieved_post.metadata.title = "Updated Test Blog Post"
    storage.blog_posts.update(post_id, retrieved_post)
    print(f"Updated blog post title: {retrieved_post.metadata.title}")
    
    # Get all
    all_posts = storage.blog_posts.get_all()
    print(f"Total blog posts: {len(all_posts)}")
    
    # Search
    search_results = storage.blog_posts.search()
    print(f"Search results: {len(search_results)}")
    
    # Delete
    storage.blog_posts.delete(post_id)
    print(f"Deleted blog post")
    
    # Test other storage types
    print("\nTesting other storage types...")
    
    # Test SEOAuditResult storage
    seo_score = {
        "overall": 85.5,
        "readability": 90.0,
        "keyword_density": 80.0,
        "meta_optimization": 85.0,
        "technical_seo": 87.0
    }
    
    from app.models import SEOScore, SEORecommendation, SEOAuditResult
    
    seo_audit = SEOAuditResult(
        original_content="Original content",
        optimized_content="Optimized content",
        seo_score=SEOScore(**seo_score),
        recommendations=[
            SEORecommendation(
                category="Keywords",
                issue="Low keyword density",
                suggestion="Add more primary keywords",
                priority="medium"
            )
        ],
        primary_keyword="test",
        secondary_keywords=["example", "demo"],
        improvements_summary="Improved keyword usage"
    )
    
    audit_id = storage.seo_audits.create(seo_audit)
    print(f"Created SEO audit with ID: {audit_id}")
    
    # Test backup
    storage.backup()
    print("Backup created successfully")
    
    print("\nAll storage tests completed successfully!")