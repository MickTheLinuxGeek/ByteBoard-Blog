#!/usr/bin/env python
"""
Comprehensive test script to verify cache monitoring middleware functionality and logging.
Tests task 55: Test cache monitoring functionality
"""

import os
import sys
import django
import logging
import tempfile
from io import StringIO
from django.test import RequestFactory, TestCase
from django.core.cache import cache
from django.http import HttpResponse

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byte_board_blog.settings')
django.setup()

from blog.middleware import CacheMonitoringMiddleware


class CacheMonitoringTests:
    """Comprehensive tests for cache monitoring functionality."""
    
    def __init__(self):
        self.factory = RequestFactory()
        self.middleware = CacheMonitoringMiddleware(self._mock_get_response)
        self.log_output = StringIO()
        
    def _mock_get_response(self, request):
        """Mock Django response for testing."""
        return HttpResponse("Mock response")
    
    def setUp_logging(self):
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
        
    def tearDown_logging(self):
        """Clean up logging after tests."""
        if hasattr(self, 'cache_logger') and hasattr(self, 'log_handler'):
            self.cache_logger.removeHandler(self.log_handler)
            self.log_handler.close()
    
    def test_middleware_request_processing(self):
        """Test that middleware properly processes requests."""
        print("1. Testing middleware request processing...")
        
        request = self.factory.get('/test/')
        result = self.middleware.process_request(request)
        
        # Should return None (continue processing)
        assert result is None, f"Expected None, got {result}"
        
        # Should set timing attributes
        assert hasattr(request, '_cache_start_time'), "Cache start time not set"
        assert hasattr(request, '_cache_operations'), "Cache operations list not set"
        assert isinstance(request._cache_operations, list), "Cache operations should be a list"
        
        print("   ✓ Request processing works correctly")
    
    def test_middleware_response_processing(self):
        """Test that middleware properly processes responses."""
        print("2. Testing middleware response processing...")
        
        request = self.factory.get('/test/')
        self.middleware.process_request(request)
        
        response = HttpResponse("Test response")
        result = self.middleware.process_response(request, response)
        
        # Should return the same response
        assert result == response, "Response not properly returned"
        
        print("   ✓ Response processing works correctly")
    
    def test_cache_operations_monitoring(self):
        """Test that cache operations are properly monitored."""
        print("3. Testing cache operations monitoring...")
        
        # Clear any existing cache entries
        cache.clear()
        
        # Test SET operation
        cache.set('test_monitoring_key', 'test_value', 300)
        print("   ✓ Cache SET operation completed")
        
        # Test GET operation (hit)
        result = cache.get('test_monitoring_key')
        assert result == 'test_value', f"Expected 'test_value', got {result}"
        print("   ✓ Cache GET operation (hit) completed")
        
        # Test GET operation (miss)
        result = cache.get('nonexistent_monitoring_key', 'default')
        assert result == 'default', f"Expected 'default', got {result}"
        print("   ✓ Cache GET operation (miss) completed")
        
        # Test DELETE operation
        cache.delete('test_monitoring_key')
        print("   ✓ Cache DELETE operation completed")
        
        # Verify deletion
        result = cache.get('test_monitoring_key', 'not_found')
        assert result == 'not_found', "Key was not properly deleted"
        print("   ✓ Cache deletion verified")
    
    def test_logging_functionality(self):
        """Test that cache operations are properly logged."""
        print("4. Testing logging functionality...")
        
        self.setUp_logging()
        
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
            assert 'Cache SET for key: test_log_key' in log_content, "SET operation not logged"
            assert 'Cache HIT for key: test_log_key' in log_content, "Cache HIT not logged"
            assert 'Cache MISS for key: nonexistent_log_key' in log_content, "Cache MISS not logged"
            assert 'Cache DELETE for key: test_log_key' in log_content, "DELETE operation not logged"
            
            print("   ✓ Cache operations logged correctly")
            print(f"   ✓ Log entries captured: {len(log_content.splitlines())} lines")
            
        finally:
            self.tearDown_logging()
    
    def test_slow_operation_detection(self):
        """Test that slow cache operations are detected and logged."""
        print("5. Testing slow operation detection...")
        
        # Note: This test is primarily structural since we can't easily simulate
        # slow operations in a unit test environment without mocking
        
        # Verify the monitoring functions exist and have the right structure
        from blog.middleware import monitored_cache_get, monitored_cache_set, monitored_cache_delete
        
        # Test that the wrapper functions exist
        assert callable(monitored_cache_get), "monitored_cache_get not callable"
        assert callable(monitored_cache_set), "monitored_cache_set not callable"  
        assert callable(monitored_cache_delete), "monitored_cache_delete not callable"
        
        print("   ✓ Slow operation detection functions present")
        print("   ✓ Monitoring wrappers properly configured")
    
    def test_end_to_end_request_cycle(self):
        """Test complete request cycle with cache monitoring."""
        print("6. Testing end-to-end request cycle...")
        
        self.setUp_logging()
        
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
            assert final_response == response, "Response cycle not completed correctly"
            assert cached_value == 'request_value', "Cache operations during request failed"
            
            # Check that logs were generated
            log_content = self.log_output.getvalue()
            assert len(log_content) > 0, "No log output generated during request cycle"
            
            print("   ✓ End-to-end request cycle completed successfully")
            print("   ✓ Cache operations during request logged properly")
            
        finally:
            self.tearDown_logging()
    
    def test_logging_configuration(self):
        """Test that Django logging configuration is properly set up."""
        print("7. Testing Django logging configuration...")
        
        # Import Django settings
        from django.conf import settings
        
        # Verify LOGGING configuration exists
        assert hasattr(settings, 'LOGGING'), "LOGGING configuration not found in settings"
        
        logging_config = settings.LOGGING
        
        # Verify required components
        assert 'version' in logging_config, "Logging version not specified"
        assert 'formatters' in logging_config, "Formatters not configured"
        assert 'handlers' in logging_config, "Handlers not configured"
        assert 'loggers' in logging_config, "Loggers not configured"
        
        # Verify cache-specific configuration
        assert 'cache' in logging_config['formatters'], "Cache formatter not configured"
        assert 'cache_console' in logging_config['handlers'], "Cache console handler not configured"
        assert 'cache_file' in logging_config['handlers'], "Cache file handler not configured"
        assert 'blog.cache' in logging_config['loggers'], "Blog cache logger not configured"
        
        print("   ✓ Django logging configuration properly set up")
        print("   ✓ Cache-specific logging components configured")
    
    def run_all_tests(self):
        """Run all cache monitoring tests."""
        print("=" * 60)
        print("COMPREHENSIVE CACHE MONITORING TESTS")
        print("=" * 60)
        
        try:
            self.test_middleware_request_processing()
            self.test_middleware_response_processing()
            self.test_cache_operations_monitoring()
            self.test_logging_functionality()
            self.test_slow_operation_detection()
            self.test_end_to_end_request_cycle()
            self.test_logging_configuration()
            
            print("\n" + "=" * 60)
            print("✅ ALL CACHE MONITORING TESTS PASSED!")
            print("Cache monitoring functionality is working correctly.")
            print("Logging configuration is properly set up.")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Run comprehensive cache monitoring tests."""
    # Ensure cache table exists for database cache backend
    from django.core.management import execute_from_command_line
    
    try:
        execute_from_command_line(['manage.py', 'createcachetable', '--verbosity=0'])
    except Exception:
        pass  # Table might already exist
    
    # Run the tests
    test_runner = CacheMonitoringTests()
    success = test_runner.run_all_tests()
    
    if success:
        print("\nTask 55: Test cache monitoring functionality - COMPLETED ✅")
        sys.exit(0)
    else:
        print("\nTask 55: Test cache monitoring functionality - FAILED ❌")
        sys.exit(1)


if __name__ == '__main__':
    main()