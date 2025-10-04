"""
Test Post content caching functionality.

This test module verifies that the Post.get_cached_content() method
correctly uses caching for markdown content rendering.
"""

from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User
from blog.models import Post


class PostContentCacheTestCase(TestCase):
    """Test Post content caching functionality."""
    
    def setUp(self):
        """Set up test data and clear cache before each test."""
        cache.clear()
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # Create a test post with markdown content
        markdown_content = """
# Test Post Content

This is a **test post** with *markdown* formatting to verify that the content caching functionality works correctly.

## Features to test:
- Bold and italic text
- Headers
- Lists

```python
def hello_world():
    print("Hello, World!")
```

The caching should work for all markdown rendering.
"""
        
        self.post = Post.objects.create(
            title="Test Post for Content Caching",
            slug="test-post-content-caching",
            author=self.user,
            content=markdown_content,
            status="published"
        )
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_first_access_generates_and_caches_content(self):
        """Test that first access generates and caches the content."""
        cache_key = f"post_content_{self.post.id}"
        
        # Clear any existing cache for this post
        cache.delete(cache_key)
        
        # First access should generate and cache the content
        content1 = self.post.get_cached_content()
        
        # Verify content was generated
        self.assertIsNotNone(content1,
                            "Content should be generated")
        self.assertGreater(len(content1), 0,
                          "Content should not be empty")
        
        # Check if it was cached
        cached_value = cache.get(cache_key)
        self.assertIsNotNone(cached_value,
                            "Content should be cached after first access")
        self.assertEqual(cached_value, content1,
                        "Cached value should match generated content")
    
    def test_second_access_uses_cached_version(self):
        """Test that second access uses cached version."""
        cache_key = f"post_content_{self.post.id}"
        
        # First access to populate cache
        content1 = self.post.get_cached_content()
        
        # Second access should use cached version
        content2 = self.post.get_cached_content()
        
        # Verify contents match
        self.assertEqual(content1, content2,
                        "Second access should return same content as first")
        
        # Verify cache still exists
        cached_value = cache.get(cache_key)
        self.assertIsNotNone(cached_value,
                            "Cache should still exist after second access")
        self.assertEqual(cached_value, content2,
                        "Cached value should match returned content")
    
    def test_markdown_rendered_to_html(self):
        """Test that markdown content is rendered to HTML."""
        content = self.post.get_cached_content()
        
        # Check if content contains HTML tags (markdown was rendered)
        has_html_tags = '<' in content and '>' in content
        self.assertTrue(has_html_tags,
                       "Content should contain HTML tags (markdown rendered)")
        
        # Verify specific markdown features were rendered
        # Headers should be converted to <h1>, <h2>, etc. (with possible attributes)
        content_lower = content.lower()
        self.assertTrue('<h1' in content_lower and '</h1>' in content_lower,
                       "H1 headers should be rendered")
        self.assertTrue('<h2' in content_lower and '</h2>' in content_lower,
                       "H2 headers should be rendered")
    
    def test_cache_key_format(self):
        """Test that cache key follows the correct format."""
        cache_key = f"post_content_{self.post.id}"
        
        # Access content to populate cache
        _ = self.post.get_cached_content()
        
        # Verify cache key exists with correct format
        cached_value = cache.get(cache_key)
        self.assertIsNotNone(cached_value,
                            f"Cache key should follow format: post_content_{{post_id}}")
        
        # Verify wrong key doesn't exist
        wrong_key = f"post_{self.post.id}"
        self.assertIsNone(cache.get(wrong_key),
                         "Cache should not exist under wrong key format")
    
    def test_cache_ttl_is_set(self):
        """Test that cache TTL is set correctly."""
        cache_key = f"post_content_{self.post.id}"
        
        # Access content to populate cache
        _ = self.post.get_cached_content()
        
        # Verify cache key still exists (TTL working)
        cached_value = cache.get(cache_key)
        self.assertIsNotNone(cached_value,
                            "Cache key should exist (TTL set correctly)")
    
    def test_cache_invalidation_on_post_save(self):
        """Test that cache is invalidated when post is saved."""
        cache_key = f"post_content_{self.post.id}"
        
        # Populate cache
        content1 = self.post.get_cached_content()
        
        # Verify cache exists
        self.assertIsNotNone(cache.get(cache_key))
        
        # Update the post (should trigger cache invalidation)
        self.post.content = "# Updated Content\n\nThis is updated content."
        self.post.save()
        
        # Verify cache was invalidated
        self.assertIsNone(cache.get(cache_key),
                         "Cache should be invalidated after post save")
        
        # Get new content (should be different)
        content2 = self.post.get_cached_content()
        self.assertNotEqual(content1, content2,
                          "New content should be different after update")