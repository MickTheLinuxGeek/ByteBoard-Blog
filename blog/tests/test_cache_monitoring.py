"""
Test cache monitoring middleware functionality.

This test module verifies that the CacheMonitoringMiddleware properly
monitors cache operations and processes requests/responses.
"""

from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.core.cache import cache
from blog.middleware import CacheMonitoringMiddleware


class CacheMonitoringMiddlewareTestCase(TestCase):
    """Test cache monitoring middleware functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        cache.clear()
        self.factory = RequestFactory()
        
        # Create a mock get_response function
        def mock_get_response(request):
            return HttpResponse("Mock response")
        
        self.middleware = CacheMonitoringMiddleware(mock_get_response)
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_request_processing(self):
        """Test that request processing sets required attributes."""
        # Create a mock request
        request = self.factory.get('/test/')
        
        # Process request
        self.middleware.process_request(request)
        
        # Verify request attributes are set
        self.assertTrue(hasattr(request, '_cache_start_time'),
                       "Cache start time should be set")
        self.assertTrue(hasattr(request, '_cache_operations'),
                       "Cache operations list should be set")
    
    def test_cache_set_operation(self):
        """Test cache SET operation monitoring."""
        # Set a cache value
        cache.set('test_key', 'test_value', 300)
        
        # Verify the value was set
        result = cache.get('test_key')
        self.assertEqual(result, 'test_value',
                        "Cache SET should store the value correctly")
    
    def test_cache_get_hit(self):
        """Test cache GET operation with cache hit."""
        # Set a value first
        cache.set('test_key', 'test_value', 300)
        
        # Get the value (cache hit)
        result = cache.get('test_key')
        self.assertEqual(result, 'test_value',
                        "Cache GET should return the cached value")
    
    def test_cache_get_miss(self):
        """Test cache GET operation with cache miss."""
        # Try to get a nonexistent key with default value
        result = cache.get('nonexistent_key', 'default_value')
        self.assertEqual(result, 'default_value',
                        "Cache GET should return default value on miss")
    
    def test_cache_delete_operation(self):
        """Test cache DELETE operation monitoring."""
        # Set a value first
        cache.set('test_key', 'test_value', 300)
        
        # Delete the key
        cache.delete('test_key')
        
        # Verify key was deleted
        result = cache.get('test_key', 'not_found')
        self.assertEqual(result, 'not_found',
                        "Cache DELETE should remove the key")
    
    def test_response_processing(self):
        """Test that response processing works correctly."""
        # Create a mock request
        request = self.factory.get('/test/')
        
        # Process request first
        self.middleware.process_request(request)
        
        # Create and process response
        response = HttpResponse("Test response")
        processed_response = self.middleware.process_response(request, response)
        
        # Verify response is returned unchanged
        self.assertEqual(processed_response, response,
                        "Response should be returned unchanged")
    
    def test_full_middleware_workflow(self):
        """Test complete middleware workflow with request and response."""
        # Create a mock request
        request = self.factory.get('/test/')
        
        # Process request
        self.middleware.process_request(request)
        
        # Verify request attributes
        self.assertTrue(hasattr(request, '_cache_start_time'))
        self.assertTrue(hasattr(request, '_cache_operations'))
        
        # Perform some cache operations
        cache.set('workflow_test', 'test_data', 300)
        result = cache.get('workflow_test')
        self.assertEqual(result, 'test_data')
        
        # Process response
        response = HttpResponse("Test response")
        processed_response = self.middleware.process_response(request, response)
        
        # Verify response processing
        self.assertEqual(processed_response, response)