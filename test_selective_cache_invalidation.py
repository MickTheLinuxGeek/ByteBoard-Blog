#!/usr/bin/env python
"""
Test script to verify selective cache invalidation patterns work correctly.

This script tests the pattern matching functionality for cache invalidation,
ensuring that only targeted cache keys are invalidated while others remain.
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
from blog.signals import (
    invalidate_cache_pattern,
    invalidate_post_related_caches,
    invalidate_category_related_caches,
    invalidate_tag_related_caches
)
from blog.utils import get_cached_common_context


def setup_test_data():
    """Setup test data and populate various caches."""
    print("=== Setting Up Test Data ===")
    
    # Create test user if needed
    user, created = User.objects.get_or_create(
        username='testuser_selective',
        defaults={'email': 'selective@example.com', 'password': 'testpass'}
    )
    
    # Clean up any existing test data
    Post.objects.filter(title__startswith="Selective Test").delete()
    Category.objects.filter(name__startswith="Selective Test").delete()
    Tag.objects.filter(name__startswith="selective-test").delete()
    
    # Create test post
    post = Post.objects.create(
        title="Selective Test Post",
        content="This is a test post for selective cache invalidation.",
        author=user,
        status="published"
    )
    
    # Create test category
    category = Category.objects.create(name="Selective Test Category")
    
    # Create test tag
    tag = Tag.objects.create(name="selective-test-tag")
    
    # Populate all caches
    _ = post.summary  # Cache post_summary_{id}
    _ = post.get_cached_content()  # Cache post_content_{id}
    _ = get_cached_common_context()  # Cache categories_all, tags_all, archive_dates
    
    # Populate template fragment caches (simulate)
    cache.set("categories_sidebar", "categories content", 3600)
    cache.set("tags_sidebar", "tags content", 3600)
    cache.set("archive_sidebar", "archive content", 3600)
    
    # Add some unrelated caches that should not be affected
    cache.set("unrelated_cache_1", "some data", 3600)
    cache.set("unrelated_cache_2", "other data", 3600)
    cache.set("user_session_123", "session data", 3600)
    
    print("✓ Test data and caches populated")
    return post, category, tag


def test_pattern_matching_function():
    """Test the basic pattern matching function."""
    print("\n=== Testing Pattern Matching Function ===")
    
    # Setup specific test caches
    cache.set("test_post_123", "data", 3600)
    cache.set("test_post_456", "data", 3600)
    cache.set("test_category_789", "data", 3600)
    cache.set("unrelated_test", "data", 3600)
    
    # Verify caches exist
    assert cache.get("test_post_123") is not None, "Test post cache should exist"
    assert cache.get("test_post_456") is not None, "Test post cache should exist"
    assert cache.get("test_category_789") is not None, "Test category cache should exist"
    assert cache.get("unrelated_test") is not None, "Unrelated cache should exist"
    
    # Test pattern matching - invalidate test_post_* pattern
    invalidate_cache_pattern("test_post_*")
    
    # Verify only post caches are invalidated
    assert cache.get("test_post_123") is None, "test_post_123 should be invalidated"
    assert cache.get("test_post_456") is None, "test_post_456 should be invalidated"
    assert cache.get("test_category_789") is not None, "test_category_789 should remain"
    assert cache.get("unrelated_test") is not None, "unrelated_test should remain"
    
    print("✓ Pattern matching function works correctly")


def test_selective_post_invalidation():
    """Test selective invalidation of post-related caches."""
    print("\n=== Testing Selective Post Invalidation ===")
    
    post, category, tag = setup_test_data()
    
    # Verify all caches exist before invalidation
    assert cache.get(f"post_summary_{post.id}") is not None, "Post summary should exist"
    assert cache.get(f"post_content_{post.id}") is not None, "Post content should exist"
    assert cache.get("categories_all") is not None, "Categories should exist"
    assert cache.get("tags_all") is not None, "Tags should exist"
    assert cache.get("unrelated_cache_1") is not None, "Unrelated cache should exist"
    
    # Use selective post invalidation
    invalidate_post_related_caches()
    
    # Verify only post-related caches are invalidated
    assert cache.get(f"post_summary_{post.id}") is None, "Post summary should be invalidated"
    assert cache.get(f"post_content_{post.id}") is None, "Post content should be invalidated"
    assert cache.get("archive_dates") is None, "Archive dates should be invalidated"
    assert cache.get("archive_sidebar") is None, "Archive sidebar should be invalidated"
    
    # Verify other caches remain
    assert cache.get("categories_all") is not None, "Categories should remain"
    assert cache.get("tags_all") is not None, "Tags should remain"
    assert cache.get("categories_sidebar") is not None, "Categories sidebar should remain"
    assert cache.get("tags_sidebar") is not None, "Tags sidebar should remain"
    assert cache.get("unrelated_cache_1") is not None, "Unrelated cache should remain"
    
    print("✓ Selective post invalidation works correctly")


def test_selective_category_invalidation():
    """Test selective invalidation of category-related caches."""
    print("\n=== Testing Selective Category Invalidation ===")
    
    post, category, tag = setup_test_data()
    
    # Verify all caches exist before invalidation
    assert cache.get("categories_all") is not None, "Categories should exist"
    assert cache.get("categories_sidebar") is not None, "Categories sidebar should exist"
    assert cache.get("tags_all") is not None, "Tags should exist"
    assert cache.get(f"post_summary_{post.id}") is not None, "Post summary should exist"
    
    # Use selective category invalidation
    invalidate_category_related_caches()
    
    # Verify only category-related caches are invalidated
    assert cache.get("categories_all") is None, "Categories should be invalidated"
    assert cache.get("categories_sidebar") is None, "Categories sidebar should be invalidated"
    
    # Verify other caches remain
    assert cache.get("tags_all") is not None, "Tags should remain"
    assert cache.get("tags_sidebar") is not None, "Tags sidebar should remain"
    assert cache.get(f"post_summary_{post.id}") is not None, "Post summary should remain"
    assert cache.get("unrelated_cache_1") is not None, "Unrelated cache should remain"
    
    print("✓ Selective category invalidation works correctly")


def test_selective_tag_invalidation():
    """Test selective invalidation of tag-related caches."""
    print("\n=== Testing Selective Tag Invalidation ===")
    
    post, category, tag = setup_test_data()
    
    # Verify all caches exist before invalidation
    assert cache.get("tags_all") is not None, "Tags should exist"
    assert cache.get("tags_sidebar") is not None, "Tags sidebar should exist"
    assert cache.get("categories_all") is not None, "Categories should exist"
    assert cache.get(f"post_summary_{post.id}") is not None, "Post summary should exist"
    
    # Use selective tag invalidation
    invalidate_tag_related_caches()
    
    # Verify only tag-related caches are invalidated
    assert cache.get("tags_all") is None, "Tags should be invalidated"
    assert cache.get("tags_sidebar") is None, "Tags sidebar should be invalidated"
    
    # Verify other caches remain
    assert cache.get("categories_all") is not None, "Categories should remain"
    assert cache.get("categories_sidebar") is not None, "Categories sidebar should remain"
    assert cache.get(f"post_summary_{post.id}") is not None, "Post summary should remain"
    assert cache.get("unrelated_cache_1") is not None, "Unrelated cache should remain"
    
    print("✓ Selective tag invalidation works correctly")


def test_cache_isolation():
    """Test that unrelated caches are never affected by selective invalidation."""
    print("\n=== Testing Cache Isolation ===")
    
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
        assert cache.get(key) is not None, f"{key} should be cached"
    
    # Run all selective invalidation functions
    invalidate_post_related_caches()
    invalidate_category_related_caches() 
    invalidate_tag_related_caches()
    
    # Verify all unrelated caches still exist
    for key in unrelated_caches.keys():
        assert cache.get(key) is not None, f"{key} should remain after selective invalidation"
    
    print("✓ Cache isolation works correctly - unrelated caches preserved")


def cleanup_test_data():
    """Clean up test data."""
    print("\n=== Cleaning Up Test Data ===")
    
    # Clean up test data
    Post.objects.filter(title__startswith="Selective Test").delete()
    Category.objects.filter(name__startswith="Selective Test").delete()
    Tag.objects.filter(name__startswith="selective-test").delete()
    User.objects.filter(username='testuser_selective').delete()
    
    # Clear all caches to clean state
    cache.clear()
    
    print("✓ Test data cleaned up")


if __name__ == "__main__":
    print("Starting selective cache invalidation tests...")
    
    try:
        test_pattern_matching_function()
        test_selective_post_invalidation()
        test_selective_category_invalidation()
        test_selective_tag_invalidation()
        test_cache_isolation()
        
        print("\n🎉 All selective cache invalidation tests passed!")
        print("Pattern-based cache invalidation is working correctly.")
        print("Cache isolation is maintained - unrelated caches are preserved.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
    finally:
        cleanup_test_data()