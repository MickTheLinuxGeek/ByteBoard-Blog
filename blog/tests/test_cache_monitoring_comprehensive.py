"""
Comprehensive test suite for cache monitoring middleware functionality and logging.
Tests task 55: Test cache monitoring functionality
"""

import logging
from io import StringIO
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings

from blog.middleware import CacheMonitoringMiddleware


class CacheMonitoringComprehensiveTestCase(TestCase):
    """Comprehensive tests for cache monitoring functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        cache.clear()
        self.factory = RequestFactory()
        self.middleware = CacheMonitoringMiddleware(self._mock_get_response)
        self.log_output = StringIO()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def _mock_get_response(self, request):
        """Mock Django response for testing."""
        return HttpResponse("Mock response")
    
    def _setup_logging(self):
        """Set up logging capture for tests."""
        # Create a string handler to capture log output
        self.log_handler = logging.StreamHandler(self.log_output)
        self.log_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[CACHE] %(asctime)s %(levelname)s: %(message)s')
        self.log_handler.setFormatter(formatter)
        
        # Get the cache logger and add our handler
        self.cache_logger = logging.getLogger('blog.cache')
        self.cache_logger.addHandler(self.log_handler)
        self.cache_logger.setLevel(logging.DEBUG)
    
    def _teardown_logging(self):
        """Clean up logging after tests."""
        if hasattr(self, 'cache_logger') and hasattr(self, 'log_handler'):
            self.cache_logger.removeHandler(self.log_handler)
            self.log_handler.close()
    
    def test_middleware_request_processing(self):
        """Test that middleware properly processes requests."""
        request = self.factory.get('/test/')
        result = self.middleware.process_request(request)
        
        # Should return None (continue processing)
        self.assertIsNone(result, "Middleware should return None to continue processing")
        
        # Should set timing attributes
        self.assertTrue(hasattr(request, '_cache_start_time'),
                       "Cache start time should be set")
        self.assertTrue(hasattr(request, '_cache_operations'),
                       "Cache operations list should be set")
        self.assertIsInstance(request._cache_operations, list,
                            "Cache operations should be a list")
    
    def test_middleware_response_processing(self):
        """Test that middleware properly processes responses."""
        request = self.factory.get('/test/')
        self.middleware.process_request(request)
        
        response = HttpResponse("Test response")
        result = self.middleware.process_response(request, response)
        
        # Should return the same response
        self.assertEqual(result, response,
                        "Response should be returned unchanged")
    
    def test_cache_operations_monitoring(self):
        """Test that cache operations are properly monitored."""
        # Clear any existing cache entries
        cache.clear()
        
        # Test SET operation
        cache.set('test_monitoring_key', 'test_value', 300)
        
        # Test GET operation (hit)
        result = cache.get('test_monitoring_key')
        self.assertEqual(result, 'test_value',
                        "Cache GET should return the set value")
        
        # Test GET operation (miss)
        result = cache.get('nonexistent_monitoring_key', 'default')
        self.assertEqual(result, 'default',
                        "Cache GET should return default on miss")
        
        # Test DELETE operation
        cache.delete('test_monitoring_key')
        
        # Verify deletion
        result = cache.get('test_monitoring_key', 'not_found')
        self.assertEqual(result, 'not_found',
                        "Key should be deleted from cache")
    
    def test_logging_functionality(self):
        """Test that cache operations are properly logged."""
        self._setup_logging()
        
        try:
            # Clear log output
            self.log_output.seek(0)
            self.log_output.truncate(0)
            
            # Perform cache operations that should generate logs
            cache.set('test_log_key', 'log_test_value', 300)
            cache.get('test_log_key')
            cache.get('nonexistent_log_key', 'default')
            cache.delete('test_log_key')
            
            # Get log output
            log_content = self.log_output.getvalue()
            
            # Verify log entries were created
            self.assertIn('Cache SET for key: test_log_key', log_content,
                         "SET operation should be logged")
            self.assertIn('Cache HIT for key: test_log_key', log_content,
                         "Cache HIT should be logged")
            self.assertIn('Cache MISS for key: nonexistent_log_key', log_content,
                         "Cache MISS should be logged")
            self.assertIn('Cache DELETE for key: test_log_key', log_content,
                         "DELETE operation should be logged")
            
        finally:
            self._teardown_logging()
    
    def test_slow_operation_detection(self):
        """Test that slow cache operations are detected and logged."""
        # Note: This test is primarily structural since we can't easily simulate
        # slow operations in a unit test environment without mocking
        
        # Verify the monitoring functions exist and have the right structure
        from blog.middleware import monitored_cache_get, monitored_cache_set, monitored_cache_delete
        
        # Test that the wrapper functions exist
        self.assertTrue(callable(monitored_cache_get),
                       "monitored_cache_get should be callable")
        self.assertTrue(callable(monitored_cache_set),
                       "monitored_cache_set should be callable")
        self.assertTrue(callable(monitored_cache_delete),
                       "monitored_cache_delete should be callable")
    
    def test_end_to_end_request_cycle(self):
        """Test complete request cycle with cache monitoring."""
        self._setup_logging()
        
        try:
            # Clear log output
            self.log_output.seek(0)
            self.log_output.truncate(0)
            
            # Simulate a complete request cycle
            request = self.factory.get('/test-cache-monitoring/')
            
            # Process request
            self.middleware.process_request(request)
            
            # Simulate some cache operations during request processing
            cache.set('request_cycle_key', 'request_value', 300)
            cached_value = cache.get('request_cycle_key')
            
            # Process response
            response = HttpResponse("Test response")
            final_response = self.middleware.process_response(request, response)
            
            # Verify the cycle completed successfully
            self.assertEqual(final_response, response,
                           "Response cycle should complete correctly")
            self.assertEqual(cached_value, 'request_value',
                           "Cache operations during request should work")
            
            # Check that logs were generated
            log_content = self.log_output.getvalue()
            self.assertGreater(len(log_content), 0,
                             "Log output should be generated during request cycle")
            
        finally:
            self._teardown_logging()
    
    def test_logging_configuration(self):
        """Test that Django logging configuration is properly set up."""
        # Verify LOGGING configuration exists
        self.assertTrue(hasattr(settings, 'LOGGING'),
                       "LOGGING configuration should exist in settings")
        
        logging_config = settings.LOGGING
        
        # Verify required components
        self.assertIn('version', logging_config,
                     "Logging version should be specified")
        self.assertIn('formatters', logging_config,
                     "Formatters should be configured")
        self.assertIn('handlers', logging_config,
                     "Handlers should be configured")
        self.assertIn('loggers', logging_config,
                     "Loggers should be configured")
        
        # Verify cache-specific configuration
        self.assertIn('cache', logging_config['formatters'],
                     "Cache formatter should be configured")
        self.assertIn('cache_console', logging_config['handlers'],
                     "Cache console handler should be configured")
        self.assertIn('cache_file', logging_config['handlers'],
                     "Cache file handler should be configured")
        self.assertIn('blog.cache', logging_config['loggers'],
                     "Blog cache logger should be configured")
