"""
Test Post summary caching functionality.

This test module verifies that the Post.summary property
correctly uses caching for summary generation.
"""

from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User
from blog.models import Post


class PostSummaryCacheTestCase(TestCase):
    """Test Post summary caching functionality."""
    
    def setUp(self):
        """Set up test data and clear cache before each test."""
        cache.clear()
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # Create a test post with sufficient content
        self.post = Post.objects.create(
            title="Test Post for Summary Caching",
            slug="test-post-summary-caching",
            author=self.user,
            content="This is a test post with some content to verify that the summary caching functionality works correctly. It has more than 30 words to test the truncation feature as well. This ensures we can properly test the caching behavior.",
            status="published"
        )
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_first_access_generates_and_caches_summary(self):
        """Test that first access generates and caches the summary."""
        cache_key = f"post_summary_{self.post.id}"
        
        # Clear any existing cache for this post
        cache.delete(cache_key)
        
        # First access should generate and cache the summary
        summary1 = self.post.summary
        
        # Verify summary was generated
        self.assertIsNotNone(summary1,
                            "Summary should be generated")
        self.assertGreater(len(summary1), 0,
                          "Summary should not be empty")
        
        # Check if it was cached
        cached_value = cache.get(cache_key)
        self.assertIsNotNone(cached_value,
                            "Summary should be cached after first access")
        self.assertEqual(cached_value, summary1,
                        "Cached value should match generated summary")
    
    def test_second_access_uses_cached_version(self):
        """Test that second access uses cached version."""
        cache_key = f"post_summary_{self.post.id}"
        
        # First access to populate cache
        summary1 = self.post.summary
        
        # Second access should use cached version
        summary2 = self.post.summary
        
        # Verify summaries match
        self.assertEqual(summary1, summary2,
                        "Second access should return same summary as first")
        
        # Verify cache still exists
        cached_value = cache.get(cache_key)
        self.assertIsNotNone(cached_value,
                            "Cache should still exist after second access")
        self.assertEqual(cached_value, summary2,
                        "Cached value should match returned summary")
    
    def test_cache_key_format(self):
        """Test that cache key follows the correct format."""
        cache_key = f"post_summary_{self.post.id}"
        
        # Access summary to populate cache
        _ = self.post.summary
        
        # Verify cache key exists with correct format
        cached_value = cache.get(cache_key)
        self.assertIsNotNone(cached_value,
                            f"Cache key should follow format: post_summary_{{post_id}}")
        
        # Verify wrong key doesn't exist
        wrong_key = f"summary_{self.post.id}"
        self.assertIsNone(cache.get(wrong_key),
                         "Cache should not exist under wrong key format")
    
    def test_cache_ttl_is_set(self):
        """Test that cache TTL is set correctly."""
        cache_key = f"post_summary_{self.post.id}"
        
        # Access summary to populate cache
        _ = self.post.summary
        
        # Verify cache key still exists (TTL working)
        cached_value = cache.get(cache_key)
        self.assertIsNotNone(cached_value,
                            "Cache key should exist (TTL set correctly)")
    
    def test_cache_invalidation_on_post_save(self):
        """Test that cache is invalidated when post is saved."""
        cache_key = f"post_summary_{self.post.id}"
        
        # Populate cache
        summary1 = self.post.summary
        
        # Verify cache exists
        self.assertIsNotNone(cache.get(cache_key))
        
        # Update the post (should trigger cache invalidation)
        self.post.content = "Updated content with different text that should generate a new summary."
        self.post.save()
        
        # Verify cache was invalidated
        self.assertIsNone(cache.get(cache_key),
                         "Cache should be invalidated after post save")
        
        # Get new summary (should be different)
        summary2 = self.post.summary
        self.assertNotEqual(summary1, summary2,
                          "New summary should be different after update")
    
    def test_summary_truncation(self):
        """Test that summary is properly truncated."""
        # Access summary
        summary = self.post.summary
        
        # Verify summary is truncated (should be shorter than full content)
        self.assertLess(len(summary), len(self.post.content),
                       "Summary should be shorter than full content")
        
        # Verify summary contains content from the post
        first_words = self.post.content.split()[:5]
        for word in first_words:
            self.assertIn(word, summary,
                         f"Summary should contain word '{word}' from beginning of content")