#!/usr/bin/env python
"""
Test script to verify cache invalidation signals work correctly.

This script tests that cache entries are properly invalidated when
Post, Category, and Tag models are saved or deleted.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byte_board_blog.settings')
django.setup()

from django.core.cache import cache
from django.contrib.auth.models import User
from blog.models import Post, Category, Tag
from blog.utils import get_cached_common_context


def test_post_cache_invalidation():
    """Test that post-related caches are invalidated when a post is saved/deleted."""
    print("=== Testing Post Cache Invalidation ===")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'password': 'testpass'}
    )
    
    # Clean up any existing test posts
    Post.objects.filter(title__startswith="Test Cache Invalidation").delete()
    
    # Create a test post
    post = Post.objects.create(
        title="Test Cache Invalidation Post Signal Test",
        content="This is a test post for cache invalidation.",
        author=user,
        status="published"
    )
    
    # Populate caches
    _ = post.summary  # This should cache post_summary_{id}
    _ = post.get_cached_content()  # This should cache post_content_{id}
    _ = get_cached_common_context()  # This should cache archive_dates
    
    # Verify caches exist
    assert cache.get(f"post_summary_{post.id}") is not None, "Post summary cache should exist"
    assert cache.get(f"post_content_{post.id}") is not None, "Post content cache should exist"
    assert cache.get("archive_dates") is not None, "Archive dates cache should exist"
    print("✓ Post caches populated successfully")
    
    # Update the post (should trigger cache invalidation)
    post.title = "Updated Test Post"
    post.save()
    
    # Verify caches are invalidated
    assert cache.get(f"post_summary_{post.id}") is None, "Post summary cache should be invalidated"
    assert cache.get(f"post_content_{post.id}") is None, "Post content cache should be invalidated"
    assert cache.get("archive_dates") is None, "Archive dates cache should be invalidated"
    print("✓ Post caches invalidated successfully on save")
    
    # Repopulate caches
    _ = post.summary
    _ = post.get_cached_content()
    _ = get_cached_common_context()
    
    # Delete the post (should trigger cache invalidation)
    post_id = post.id
    post.delete()
    
    # Verify caches are invalidated after deletion
    assert cache.get(f"post_summary_{post_id}") is None, "Post summary cache should be invalidated after delete"
    assert cache.get(f"post_content_{post_id}") is None, "Post content cache should be invalidated after delete"
    assert cache.get("archive_dates") is None, "Archive dates cache should be invalidated after delete"
    print("✓ Post caches invalidated successfully on delete")


def test_category_cache_invalidation():
    """Test that category-related caches are invalidated when a category is saved/deleted."""
    print("\n=== Testing Category Cache Invalidation ===")
    
    # Clean up any existing test categories
    Category.objects.filter(name__startswith="Test Category").delete()
    
    # Create a test category
    category = Category.objects.create(
        name="Test Category Cache Invalidation"
    )
    
    # Populate caches
    _ = get_cached_common_context()  # This should cache categories_all
    cache.set("categories_sidebar", "test_sidebar_content", 3600)  # Simulate template fragment cache
    
    # Verify caches exist
    assert cache.get("categories_all") is not None, "Categories cache should exist"
    assert cache.get("categories_sidebar") is not None, "Categories sidebar cache should exist"
    print("✓ Category caches populated successfully")
    
    # Update the category (should trigger cache invalidation)
    category.name = "Updated Test Category"
    category.save()
    
    # Verify caches are invalidated
    assert cache.get("categories_all") is None, "Categories cache should be invalidated"
    assert cache.get("categories_sidebar") is None, "Categories sidebar cache should be invalidated"
    print("✓ Category caches invalidated successfully on save")
    
    # Repopulate caches
    _ = get_cached_common_context()
    cache.set("categories_sidebar", "test_sidebar_content", 3600)
    
    # Delete the category (should trigger cache invalidation)
    category.delete()
    
    # Verify caches are invalidated after deletion
    assert cache.get("categories_all") is None, "Categories cache should be invalidated after delete"
    assert cache.get("categories_sidebar") is None, "Categories sidebar cache should be invalidated after delete"
    print("✓ Category caches invalidated successfully on delete")


def test_tag_cache_invalidation():
    """Test that tag-related caches are invalidated when a tag is saved/deleted."""
    print("\n=== Testing Tag Cache Invalidation ===")
    
    # Clean up any existing test tags
    Tag.objects.filter(name__startswith="test-tag").delete()
    
    # Create a test tag
    tag = Tag.objects.create(
        name="test-tag-cache-invalidation"
    )
    
    # Populate caches
    _ = get_cached_common_context()  # This should cache tags_all
    cache.set("tags_sidebar", "test_sidebar_content", 3600)  # Simulate template fragment cache
    
    # Verify caches exist
    assert cache.get("tags_all") is not None, "Tags cache should exist"
    assert cache.get("tags_sidebar") is not None, "Tags sidebar cache should exist"
    print("✓ Tag caches populated successfully")
    
    # Update the tag (should trigger cache invalidation)
    tag.name = "updated-test-tag"
    tag.save()
    
    # Verify caches are invalidated
    assert cache.get("tags_all") is None, "Tags cache should be invalidated"
    assert cache.get("tags_sidebar") is None, "Tags sidebar cache should be invalidated"
    print("✓ Tag caches invalidated successfully on save")
    
    # Repopulate caches
    _ = get_cached_common_context()
    cache.set("tags_sidebar", "test_sidebar_content", 3600)
    
    # Delete the tag (should trigger cache invalidation)
    tag.delete()
    
    # Verify caches are invalidated after deletion
    assert cache.get("tags_all") is None, "Tags cache should be invalidated after delete"
    assert cache.get("tags_sidebar") is None, "Tags sidebar cache should be invalidated after delete"
    print("✓ Tag caches invalidated successfully on delete")


if __name__ == "__main__":
    print("Starting cache invalidation tests...")
    
    try:
        test_post_cache_invalidation()
        test_category_cache_invalidation()
        test_tag_cache_invalidation()
        
        print("\n🎉 All cache invalidation tests passed!")
        print("Signal-based cache invalidation is working correctly.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)