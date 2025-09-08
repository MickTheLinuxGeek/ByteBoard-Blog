#!/usr/bin/env python
"""
Test script to verify graceful fallback behavior when cache backend is unavailable.
Simulates cache failures and tests that the application continues to work.
"""

import os
import sys
import django
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byte_board_blog.settings')
django.setup()

from django.core.cache import cache
from django.conf import settings
from blog.utils import get_cached_common_context
from blog.models import Post, Category, Tag
from django.contrib.auth.models import User


def create_test_data():
    """Create test data for fallback testing."""
    print("Creating test data...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Create test category
    category, created = Category.objects.get_or_create(
        name='Test Category',
        defaults={'slug': 'test-category'}
    )
    
    # Create test tag
    tag, created = Tag.objects.get_or_create(
        name='Test Tag',
        defaults={'slug': 'test-tag'}
    )
    
    # Create test post
    post, created = Post.objects.get_or_create(
        title='Test Post for Fallback',
        defaults={
            'slug': 'test-post-fallback',
            'content': '# Test Content\n\nThis is a test post for fallback testing.',
            'author': user,
            'status': 'published'
        }
    )
    
    if created:
        post.categories.add(category)
        post.tags.add(tag)
    
    print(f"✓ Test data created: User, Category, Tag, Post")
    return user, category, tag, post


def test_cache_failure_simulation():
    """Test cache operations with simulated failures."""
    print("="*60)
    print("CACHE FAILURE SIMULATION TEST")
    print("="*60)
    
    # Test normal cache operations first
    print("1. Testing normal cache operations...")
    try:
        cache.set("test_key", "test_value", 60)
        value = cache.get("test_key")
        if value == "test_value":
            print("   ✓ Normal cache operations working")
        else:
            print("   ✗ Normal cache operations failed")
            return False
    except Exception as e:
        print(f"   ✗ Normal cache operations failed: {e}")
        return False
    
    # Test with cache.get raising an exception
    print("2. Testing cache.get() failure simulation...")
    with patch('django.core.cache.cache.get') as mock_get:
        mock_get.side_effect = Exception("Cache backend unavailable")
        
        try:
            # This should not raise an exception due to our fallback handling
            context = get_cached_common_context()
            if 'categories' in context and 'tags' in context and 'archive_dates' in context:
                print("   ✓ get_cached_common_context() handled cache.get() failure gracefully")
            else:
                print("   ✗ get_cached_common_context() failed with cache.get() failure")
                return False
        except Exception as e:
            print(f"   ✗ get_cached_common_context() raised exception: {e}")
            return False
    
    # Test with cache.set raising an exception
    print("3. Testing cache.set() failure simulation...")
    with patch('django.core.cache.cache.set') as mock_set:
        mock_set.side_effect = Exception("Cache backend unavailable")
        
        try:
            # This should not raise an exception due to our fallback handling
            context = get_cached_common_context()
            if 'categories' in context and 'tags' in context and 'archive_dates' in context:
                print("   ✓ get_cached_common_context() handled cache.set() failure gracefully")
            else:
                print("   ✗ get_cached_common_context() failed with cache.set() failure")
                return False
        except Exception as e:
            print(f"   ✗ get_cached_common_context() raised exception: {e}")
            return False
    
    print("✓ Cache failure simulation tests passed")
    return True


def test_post_model_fallback():
    """Test Post model caching methods with simulated failures."""
    print("\n" + "="*60)
    print("POST MODEL CACHE FALLBACK TEST")
    print("="*60)
    
    # Get test post
    try:
        post = Post.objects.get(title='Test Post for Fallback')
    except Post.DoesNotExist:
        print("✗ Test post not found, creating test data first...")
        _, _, _, post = create_test_data()
    
    # Test get_cached_content with cache.get failure
    print("1. Testing Post.get_cached_content() with cache.get() failure...")
    with patch('blog.models.cache.get') as mock_get:
        mock_get.side_effect = Exception("Cache backend unavailable")
        
        try:
            content = post.get_cached_content()
            if content and '<h1>Test Content</h1>' in content:
                print("   ✓ get_cached_content() handled cache.get() failure gracefully")
            else:
                print("   ✗ get_cached_content() failed with cache.get() failure")
                return False
        except Exception as e:
            print(f"   ✗ get_cached_content() raised exception: {e}")
            return False
    
    # Test get_cached_content with cache.set failure
    print("2. Testing Post.get_cached_content() with cache.set() failure...")
    with patch('blog.models.cache.set') as mock_set:
        mock_set.side_effect = Exception("Cache backend unavailable")
        
        try:
            content = post.get_cached_content()
            if content and '<h1>Test Content</h1>' in content:
                print("   ✓ get_cached_content() handled cache.set() failure gracefully")
            else:
                print("   ✗ get_cached_content() failed with cache.set() failure")
                return False
        except Exception as e:
            print(f"   ✗ get_cached_content() raised exception: {e}")
            return False
    
    # Test summary property with cache.get failure
    print("3. Testing Post.summary property with cache.get() failure...")
    with patch('blog.models.cache.get') as mock_get:
        mock_get.side_effect = Exception("Cache backend unavailable")
        
        try:
            summary = post.summary
            if summary and 'This is a test post' in summary:
                print("   ✓ summary property handled cache.get() failure gracefully")
            else:
                print("   ✗ summary property failed with cache.get() failure")
                return False
        except Exception as e:
            print(f"   ✗ summary property raised exception: {e}")
            return False
    
    # Test summary property with cache.set failure
    print("4. Testing Post.summary property with cache.set() failure...")
    with patch('blog.models.cache.set') as mock_set:
        mock_set.side_effect = Exception("Cache backend unavailable")
        
        try:
            summary = post.summary
            if summary and 'This is a test post' in summary:
                print("   ✓ summary property handled cache.set() failure gracefully")
            else:
                print("   ✗ summary property failed with cache.set() failure")
                return False
        except Exception as e:
            print(f"   ✗ summary property raised exception: {e}")
            return False
    
    print("✓ Post model cache fallback tests passed")
    return True


def test_complete_cache_backend_failure():
    """Test behavior when entire cache backend is unavailable."""
    print("\n" + "="*60)
    print("COMPLETE CACHE BACKEND FAILURE TEST")
    print("="*60)
    
    # Mock both cache.get and cache.set to fail
    with patch('blog.utils.cache.get') as mock_utils_get, \
         patch('blog.utils.cache.set') as mock_utils_set, \
         patch('blog.models.cache.get') as mock_models_get, \
         patch('blog.models.cache.set') as mock_models_set:
        
        mock_utils_get.side_effect = Exception("Cache backend completely unavailable")
        mock_utils_set.side_effect = Exception("Cache backend completely unavailable")
        mock_models_get.side_effect = Exception("Cache backend completely unavailable")
        mock_models_set.side_effect = Exception("Cache backend completely unavailable")
        
        print("1. Testing complete cache failure scenarios...")
        
        try:
            # Test get_cached_common_context
            context = get_cached_common_context()
            if 'categories' in context and 'tags' in context and 'archive_dates' in context:
                print("   ✓ get_cached_common_context() works without cache")
            else:
                print("   ✗ get_cached_common_context() failed without cache")
                return False
            
            # Test Post model methods
            post = Post.objects.get(title='Test Post for Fallback')
            
            content = post.get_cached_content()
            if content and '<h1>Test Content</h1>' in content:
                print("   ✓ Post.get_cached_content() works without cache")
            else:
                print("   ✗ Post.get_cached_content() failed without cache")
                return False
            
            summary = post.summary
            if summary and 'This is a test post' in summary:
                print("   ✓ Post.summary works without cache")
            else:
                print("   ✗ Post.summary failed without cache")
                return False
            
            print("✓ Application continues to work without cache backend")
            return True
            
        except Exception as e:
            print(f"✗ Application failed without cache backend: {e}")
            return False


def main():
    """Main test function."""
    print("Starting cache fallback behavior tests...")
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    print(f"Cache Backend: {settings.CACHES['default']['BACKEND']}")
    
    # Create test data
    create_test_data()
    
    # Run tests
    test1_ok = test_cache_failure_simulation()
    test2_ok = test_post_model_fallback()
    test3_ok = test_complete_cache_backend_failure()
    
    # Summary
    print("\n" + "="*60)
    print("FALLBACK TEST SUMMARY")
    print("="*60)
    print(f"Cache Failure Simulation: {'✓ PASS' if test1_ok else '✗ FAIL'}")
    print(f"Post Model Fallback: {'✓ PASS' if test2_ok else '✗ FAIL'}")
    print(f"Complete Cache Backend Failure: {'✓ PASS' if test3_ok else '✗ FAIL'}")
    
    if test1_ok and test2_ok and test3_ok:
        print("\n✓ ALL FALLBACK TESTS PASSED")
        print("✓ Application gracefully handles cache failures")
        return 0
    else:
        print("\n✗ SOME FALLBACK TESTS FAILED")
        print("✗ Check fallback implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())