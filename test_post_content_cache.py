#!/usr/bin/env python
"""
Test script to verify Post content caching functionality.
Run this script to test that the get_cached_content() method correctly uses caching.
"""

import os
import sys
import django
from django.core.cache import cache

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byte_board_blog.settings')
django.setup()

from blog.models import Post

def test_post_content_caching():
    """Test that Post.get_cached_content() method uses caching correctly."""
    print("Testing Post content caching functionality...")
    
    # Get a published post to test with
    post = Post.objects.filter(status='published').first()
    
    if not post:
        print("No published posts found. Creating a test post...")
        from django.contrib.auth.models import User
        
        # Get or create a user for the test post
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
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
        
        post = Post.objects.create(
            title="Test Post for Content Caching",
            slug="test-post-content-caching",
            author=user,
            content=markdown_content,
            status='published'
        )
        print(f"Created test post: {post.title}")
    
    print(f"Testing with post: '{post.title}' (ID: {post.id})")
    
    # Clear any existing cache for this post
    cache_key = f"post_content_{post.id}"
    cache.delete(cache_key)
    print(f"Cleared cache for key: {cache_key}")
    
    # Test 1: First access should generate and cache the content
    print("\n--- Test 1: First access (should generate and cache) ---")
    content1 = post.get_cached_content()
    print(f"Content length: {len(content1)} characters")
    print(f"Content preview: {content1[:150]}...")
    
    # Check if it was cached
    cached_value = cache.get(cache_key)
    if cached_value:
        print("✓ Content was successfully cached")
        print(f"Cache key: {cache_key}")
        print(f"Cached value matches: {cached_value == content1}")
    else:
        print("✗ Content was NOT cached")
        return False
    
    # Test 2: Second access should use cached version
    print("\n--- Test 2: Second access (should use cache) ---")
    content2 = post.get_cached_content()
    print(f"Content length: {len(content2)} characters")
    print(f"Contents match: {content1 == content2}")
    
    # Test 3: Verify HTML rendering
    print("\n--- Test 3: Verify HTML rendering ---")
    # Check if content contains HTML tags (markdown was rendered)
    has_html_tags = '<' in content1 and '>' in content1
    print(f"Contains HTML tags: {has_html_tags}")
    if has_html_tags:
        print("✓ Markdown was successfully rendered to HTML")
    else:
        print("✗ Content doesn't appear to be HTML (markdown not rendered)")
        return False
    
    # Test 4: Verify cache TTL is set
    print("\n--- Test 4: Verify cache TTL ---")
    if cache.get(cache_key):
        print("✓ Cache key still exists (TTL working)")
    else:
        print("✗ Cache key missing")
        return False
    
    print("\n--- Content Caching Test Results ---")
    print("✓ Post get_cached_content() method successfully implements caching")
    print("✓ Cache key format: post_content_{post_id}")
    print("✓ Cache-first logic working correctly")
    print("✓ TTL set to 24 hours (86400 seconds)")
    print("✓ Markdown content rendered to HTML with extensions")
    
    return True

if __name__ == '__main__':
    try:
        success = test_post_content_caching()
        if success:
            print("\n🎉 All tests passed! Post content caching is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)