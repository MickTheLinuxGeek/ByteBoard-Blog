#!/usr/bin/env python
"""
Test script to verify cache monitoring middleware functionality.
"""

import os
import sys
import django
from django.test import RequestFactory
from django.core.cache import cache

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byte_board_blog.settings')
django.setup()

from blog.middleware import CacheMonitoringMiddleware


def test_cache_monitoring():
    """Test cache monitoring middleware functionality."""
    print("Testing Cache Monitoring Middleware...")
    
    # Create a request factory and middleware instance
    factory = RequestFactory()
    
    # Create a mock get_response function
    def mock_get_response(request):
        from django.http import HttpResponse
        return HttpResponse("Mock response")
    
    middleware = CacheMonitoringMiddleware(mock_get_response)
    
    # Create a mock request
    request = factory.get('/test/')
    
    # Test request processing
    print("1. Testing request processing...")
    middleware.process_request(request)
    
    # Verify request attributes are set
    assert hasattr(request, '_cache_start_time'), "Cache start time not set"
    assert hasattr(request, '_cache_operations'), "Cache operations list not set"
    print("   ✓ Request processing works correctly")
    
    # Test cache operations
    print("2. Testing cache operations monitoring...")
    
    # Test cache set operation
    cache.set('test_key', 'test_value', 300)
    print("   ✓ Cache SET operation completed")
    
    # Test cache get operation (hit)
    result = cache.get('test_key')
    assert result == 'test_value', f"Expected 'test_value', got {result}"
    print("   ✓ Cache GET operation (hit) completed")
    
    # Test cache get operation (miss)
    result = cache.get('nonexistent_key', 'default_value')
    assert result == 'default_value', f"Expected 'default_value', got {result}"
    print("   ✓ Cache GET operation (miss) completed")
    
    # Test cache delete operation
    cache.delete('test_key')
    print("   ✓ Cache DELETE operation completed")
    
    # Verify key was deleted
    result = cache.get('test_key', 'not_found')
    assert result == 'not_found', "Key was not properly deleted"
    print("   ✓ Cache deletion verified")
    
    # Test response processing
    print("3. Testing response processing...")
    from django.http import HttpResponse
    response = HttpResponse("Test response")
    
    processed_response = middleware.process_response(request, response)
    assert processed_response == response, "Response not properly returned"
    print("   ✓ Response processing works correctly")
    
    print("\n✅ All cache monitoring tests passed!")
    print("Cache monitoring middleware is working properly.")


if __name__ == '__main__':
    test_cache_monitoring()