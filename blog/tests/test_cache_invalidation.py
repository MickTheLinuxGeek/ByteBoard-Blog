"""
Test cache invalidation signals for Post, Category, and Tag models.

This test module verifies that cache entries are properly invalidated when
Post, Category, and Tag models are saved or deleted.
"""

from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User
from blog.models import Post, Category, Tag
from blog.utils import get_cached_common_context


class PostCacheInvalidationTestCase(TestCase):
    """Test cache invalidation for Post model operations."""
    
    def setUp(self):
        """Set up test data and clear cache before each test."""
        cache.clear()
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_post_cache_invalidation_on_save(self):
        """Test that post-related caches are invalidated when a post is saved."""
        # Create a test post
        post = Post.objects.create(
            title="Test Cache Invalidation Post",
            content="This is a test post for cache invalidation.",
            author=self.user,
            status="published"
        )
        
        # Populate caches
        _ = post.summary  # This should cache post_summary_{id}
        _ = post.get_cached_content()  # This should cache post_content_{id}
        _ = get_cached_common_context()  # This should cache archive_dates
        
        # Verify caches exist
        self.assertIsNotNone(cache.get(f"post_summary_{post.id}"),
                            "Post summary cache should exist")
        self.assertIsNotNone(cache.get(f"post_content_{post.id}"),
                            "Post content cache should exist")
        self.assertIsNotNone(cache.get("archive_dates"),
                            "Archive dates cache should exist")
        
        # Update the post (should trigger cache invalidation)
        post.title = "Updated Test Post"
        post.save()
        
        # Verify caches are invalidated
        self.assertIsNone(cache.get(f"post_summary_{post.id}"),
                         "Post summary cache should be invalidated")
        self.assertIsNone(cache.get(f"post_content_{post.id}"),
                         "Post content cache should be invalidated")
        self.assertIsNone(cache.get("archive_dates"),
                         "Archive dates cache should be invalidated")
    
    def test_post_cache_invalidation_on_delete(self):
        """Test that post-related caches are invalidated when a post is deleted."""
        # Create a test post
        post = Post.objects.create(
            title="Test Cache Invalidation Post Delete",
            content="This is a test post for cache invalidation on delete.",
            author=self.user,
            status="published"
        )
        
        # Populate caches
        _ = post.summary
        _ = post.get_cached_content()
        _ = get_cached_common_context()
        
        # Verify caches exist
        self.assertIsNotNone(cache.get(f"post_summary_{post.id}"))
        self.assertIsNotNone(cache.get(f"post_content_{post.id}"))
        self.assertIsNotNone(cache.get("archive_dates"))
        
        # Delete the post (should trigger cache invalidation)
        post_id = post.id
        post.delete()
        
        # Verify caches are invalidated after deletion
        self.assertIsNone(cache.get(f"post_summary_{post_id}"),
                         "Post summary cache should be invalidated after delete")
        self.assertIsNone(cache.get(f"post_content_{post_id}"),
                         "Post content cache should be invalidated after delete")
        self.assertIsNone(cache.get("archive_dates"),
                         "Archive dates cache should be invalidated after delete")


class CategoryCacheInvalidationTestCase(TestCase):
    """Test cache invalidation for Category model operations."""
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_category_cache_invalidation_on_save(self):
        """Test that category-related caches are invalidated when a category is saved."""
        # Create a test category
        category = Category.objects.create(
            name="Test Category Cache Invalidation"
        )
        
        # Populate caches
        _ = get_cached_common_context()  # This should cache categories_all
        cache.set("categories_sidebar", "test_sidebar_content", 3600)  # Simulate template fragment cache
        
        # Verify caches exist
        self.assertIsNotNone(cache.get("categories_all"),
                            "Categories cache should exist")
        self.assertIsNotNone(cache.get("categories_sidebar"),
                            "Categories sidebar cache should exist")
        
        # Update the category (should trigger cache invalidation)
        category.name = "Updated Test Category"
        category.save()
        
        # Verify caches are invalidated
        self.assertIsNone(cache.get("categories_all"),
                         "Categories cache should be invalidated")
        self.assertIsNone(cache.get("categories_sidebar"),
                         "Categories sidebar cache should be invalidated")
    
    def test_category_cache_invalidation_on_delete(self):
        """Test that category-related caches are invalidated when a category is deleted."""
        # Create a test category
        category = Category.objects.create(
            name="Test Category Cache Invalidation Delete"
        )
        
        # Populate caches
        _ = get_cached_common_context()
        cache.set("categories_sidebar", "test_sidebar_content", 3600)
        
        # Verify caches exist
        self.assertIsNotNone(cache.get("categories_all"))
        self.assertIsNotNone(cache.get("categories_sidebar"))
        
        # Delete the category (should trigger cache invalidation)
        category.delete()
        
        # Verify caches are invalidated after deletion
        self.assertIsNone(cache.get("categories_all"),
                         "Categories cache should be invalidated after delete")
        self.assertIsNone(cache.get("categories_sidebar"),
                         "Categories sidebar cache should be invalidated after delete")


class TagCacheInvalidationTestCase(TestCase):
    """Test cache invalidation for Tag model operations."""
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_tag_cache_invalidation_on_save(self):
        """Test that tag-related caches are invalidated when a tag is saved."""
        # Create a test tag
        tag = Tag.objects.create(
            name="test-tag-cache-invalidation"
        )
        
        # Populate caches
        _ = get_cached_common_context()  # This should cache tags_all
        cache.set("tags_sidebar", "test_sidebar_content", 3600)  # Simulate template fragment cache
        
        # Verify caches exist
        self.assertIsNotNone(cache.get("tags_all"),
                            "Tags cache should exist")
        self.assertIsNotNone(cache.get("tags_sidebar"),
                            "Tags sidebar cache should exist")
        
        # Update the tag (should trigger cache invalidation)
        tag.name = "updated-test-tag"
        tag.save()
        
        # Verify caches are invalidated
        self.assertIsNone(cache.get("tags_all"),
                         "Tags cache should be invalidated")
        self.assertIsNone(cache.get("tags_sidebar"),
                         "Tags sidebar cache should be invalidated")
    
    def test_tag_cache_invalidation_on_delete(self):
        """Test that tag-related caches are invalidated when a tag is deleted."""
        # Create a test tag
        tag = Tag.objects.create(
            name="test-tag-cache-invalidation-delete"
        )
        
        # Populate caches
        _ = get_cached_common_context()
        cache.set("tags_sidebar", "test_sidebar_content", 3600)
        
        # Verify caches exist
        self.assertIsNotNone(cache.get("tags_all"))
        self.assertIsNotNone(cache.get("tags_sidebar"))
        
        # Delete the tag (should trigger cache invalidation)
        tag.delete()
        
        # Verify caches are invalidated after deletion
        self.assertIsNone(cache.get("tags_all"),
                         "Tags cache should be invalidated after delete")
        self.assertIsNone(cache.get("tags_sidebar"),
                         "Tags sidebar cache should be invalidated after delete")