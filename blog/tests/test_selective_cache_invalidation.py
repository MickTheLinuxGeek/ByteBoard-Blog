"""
Test selective cache invalidation patterns.

This test module verifies that pattern matching functionality for cache invalidation
ensures that only targeted cache keys are invalidated while others remain.
"""

from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User
from blog.models import Post, Category, Tag
from blog.signals import (
    invalidate_cache_pattern,
    invalidate_post_related_caches,
    invalidate_category_related_caches,
    invalidate_tag_related_caches
)
from blog.utils import get_cached_common_context


class SelectiveCacheInvalidationTestCase(TestCase):
    """Test selective cache invalidation functionality."""
    
    def setUp(self):
        """Set up test data and populate various caches before each test."""
        cache.clear()
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser_selective",
            email="selective@example.com",
            password="testpass123"
        )
        
        # Create test post
        self.post = Post.objects.create(
            title="Selective Test Post",
            content="This is a test post for selective cache invalidation.",
            author=self.user,
            status="published"
        )
        
        # Create test category
        self.category = Category.objects.create(name="Selective Test Category")
        
        # Create test tag
        self.tag = Tag.objects.create(name="selective-test-tag")
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def _populate_all_caches(self):
        """Helper method to populate all caches."""
        # Populate model-related caches
        _ = self.post.summary  # Cache post_summary_{id}
        _ = self.post.get_cached_content()  # Cache post_content_{id}
        _ = get_cached_common_context()  # Cache categories_all, tags_all, archive_dates
        
        # Populate template fragment caches (simulate)
        cache.set("categories_sidebar", "categories content", 3600)
        cache.set("tags_sidebar", "tags content", 3600)
        cache.set("archive_sidebar", "archive content", 3600)
        
        # Add some unrelated caches that should not be affected
        cache.set("unrelated_cache_1", "some data", 3600)
        cache.set("unrelated_cache_2", "other data", 3600)
        cache.set("user_session_123", "session data", 3600)
    
    def test_pattern_matching_function(self):
        """Test the basic pattern matching function."""
        # Setup specific test caches
        cache.set("test_post_123", "data", 3600)
        cache.set("test_post_456", "data", 3600)
        cache.set("test_category_789", "data", 3600)
        cache.set("unrelated_test", "data", 3600)
        
        # Verify caches exist
        self.assertIsNotNone(cache.get("test_post_123"),
                            "Test post cache should exist")
        self.assertIsNotNone(cache.get("test_post_456"),
                            "Test post cache should exist")
        self.assertIsNotNone(cache.get("test_category_789"),
                            "Test category cache should exist")
        self.assertIsNotNone(cache.get("unrelated_test"),
                            "Unrelated cache should exist")
        
        # Test pattern matching - invalidate test_post_* pattern
        invalidate_cache_pattern("test_post_*")
        
        # Verify only post caches are invalidated
        self.assertIsNone(cache.get("test_post_123"),
                         "test_post_123 should be invalidated")
        self.assertIsNone(cache.get("test_post_456"),
                         "test_post_456 should be invalidated")
        self.assertIsNotNone(cache.get("test_category_789"),
                            "test_category_789 should remain")
        self.assertIsNotNone(cache.get("unrelated_test"),
                            "unrelated_test should remain")
    
    def test_selective_post_invalidation(self):
        """Test selective invalidation of post-related caches."""
        self._populate_all_caches()
        
        # Verify all caches exist before invalidation
        self.assertIsNotNone(cache.get(f"post_summary_{self.post.id}"),
                            "Post summary should exist")
        self.assertIsNotNone(cache.get(f"post_content_{self.post.id}"),
                            "Post content should exist")
        self.assertIsNotNone(cache.get("categories_all"),
                            "Categories should exist")
        self.assertIsNotNone(cache.get("tags_all"),
                            "Tags should exist")
        self.assertIsNotNone(cache.get("unrelated_cache_1"),
                            "Unrelated cache should exist")
        
        # Use selective post invalidation
        invalidate_post_related_caches()
        
        # Verify only post-related caches are invalidated
        self.assertIsNone(cache.get(f"post_summary_{self.post.id}"),
                         "Post summary should be invalidated")
        self.assertIsNone(cache.get(f"post_content_{self.post.id}"),
                         "Post content should be invalidated")
        self.assertIsNone(cache.get("archive_dates"),
                         "Archive dates should be invalidated")
        self.assertIsNone(cache.get("archive_sidebar"),
                         "Archive sidebar should be invalidated")
        
        # Verify other caches remain
        self.assertIsNotNone(cache.get("categories_all"),
                            "Categories should remain")
        self.assertIsNotNone(cache.get("tags_all"),
                            "Tags should remain")
        self.assertIsNotNone(cache.get("categories_sidebar"),
                            "Categories sidebar should remain")
        self.assertIsNotNone(cache.get("tags_sidebar"),
                            "Tags sidebar should remain")
        self.assertIsNotNone(cache.get("unrelated_cache_1"),
                            "Unrelated cache should remain")
    
    def test_selective_category_invalidation(self):
        """Test selective invalidation of category-related caches."""
        self._populate_all_caches()
        
        # Verify all caches exist before invalidation
        self.assertIsNotNone(cache.get("categories_all"),
                            "Categories should exist")
        self.assertIsNotNone(cache.get("categories_sidebar"),
                            "Categories sidebar should exist")
        self.assertIsNotNone(cache.get("tags_all"),
                            "Tags should exist")
        self.assertIsNotNone(cache.get(f"post_summary_{self.post.id}"),
                            "Post summary should exist")
        
        # Use selective category invalidation
        invalidate_category_related_caches()
        
        # Verify only category-related caches are invalidated
        self.assertIsNone(cache.get("categories_all"),
                         "Categories should be invalidated")
        self.assertIsNone(cache.get("categories_sidebar"),
                         "Categories sidebar should be invalidated")
        
        # Verify other caches remain
        self.assertIsNotNone(cache.get("tags_all"),
                            "Tags should remain")
        self.assertIsNotNone(cache.get("tags_sidebar"),
                            "Tags sidebar should remain")
        self.assertIsNotNone(cache.get(f"post_summary_{self.post.id}"),
                            "Post summary should remain")
        self.assertIsNotNone(cache.get("unrelated_cache_1"),
                            "Unrelated cache should remain")
    
    def test_selective_tag_invalidation(self):
        """Test selective invalidation of tag-related caches."""
        self._populate_all_caches()
        
        # Verify all caches exist before invalidation
        self.assertIsNotNone(cache.get("tags_all"),
                            "Tags should exist")
        self.assertIsNotNone(cache.get("tags_sidebar"),
                            "Tags sidebar should exist")
        self.assertIsNotNone(cache.get("categories_all"),
                            "Categories should exist")
        self.assertIsNotNone(cache.get(f"post_summary_{self.post.id}"),
                            "Post summary should exist")
        
        # Use selective tag invalidation
        invalidate_tag_related_caches()
        
        # Verify only tag-related caches are invalidated
        self.assertIsNone(cache.get("tags_all"),
                         "Tags should be invalidated")
        self.assertIsNone(cache.get("tags_sidebar"),
                         "Tags sidebar should be invalidated")
        
        # Verify other caches remain
        self.assertIsNotNone(cache.get("categories_all"),
                            "Categories should remain")
        self.assertIsNotNone(cache.get("categories_sidebar"),
                            "Categories sidebar should remain")
        self.assertIsNotNone(cache.get(f"post_summary_{self.post.id}"),
                            "Post summary should remain")
        self.assertIsNotNone(cache.get("unrelated_cache_1"),
                            "Unrelated cache should remain")
    
    def test_cache_isolation(self):
        """Test that unrelated caches are never affected by selective invalidation."""
        # Set up various unrelated caches
        unrelated_caches = {
            "user_profile_123": "user data",
            "session_abc456": "session data",
            "external_api_cache": "api response",
            "custom_widget_data": "widget info",
            "performance_metrics": "metrics data"
        }
        
        for key, value in unrelated_caches.items():
            cache.set(key, value, 3600)
        
        # Verify all unrelated caches are set
        for key in unrelated_caches.keys():
            self.assertIsNotNone(cache.get(key),
                                f"{key} should be cached")
        
        # Run all selective invalidation functions
        invalidate_post_related_caches()
        invalidate_category_related_caches()
        invalidate_tag_related_caches()
        
        # Verify all unrelated caches still exist
        for key in unrelated_caches.keys():
            self.assertIsNotNone(cache.get(key),
                                f"{key} should remain after selective invalidation")
