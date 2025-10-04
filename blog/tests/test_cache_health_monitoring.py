"""
Test cache health monitoring functionality.
Tests cache health checks, alerting system, and monitoring middleware.
"""

import time
from unittest.mock import MagicMock
from django.test import TestCase, RequestFactory
from django.core.cache import cache

from blog.middleware import CacheHealthMonitor, CacheAlertSystem, CacheMonitoringMiddleware


class CacheHealthMonitorTestCase(TestCase):
    """
    Test CacheHealthMonitor functionality.
    
    This test case verifies that the cache health monitoring system
    properly checks cache backend health and logs status information.
    """
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_cache_health_check(self):
        """Test CacheHealthMonitor health check functionality."""
        # Test health check
        health_status = CacheHealthMonitor.check_cache_backend_health()
        
        # Verify health status structure
        required_keys = ['healthy', 'backend', 'connectivity', 'response_time', 'errors']
        for key in required_keys:
            self.assertIn(key, health_status, f"Missing key: {key}")
        
        # Verify health status types
        self.assertIsInstance(health_status['healthy'], bool)
        self.assertIsInstance(health_status['backend'], str)
        self.assertIsInstance(health_status['connectivity'], bool)
        self.assertIsInstance(health_status['errors'], list)
    
    def test_health_status_logging(self):
        """Test that health status can be logged without errors."""
        health_status = CacheHealthMonitor.check_cache_backend_health()
        
        # Test logging - should not raise any exceptions
        try:
            CacheHealthMonitor.log_health_status(health_status)
        except Exception as e:
            self.fail(f"Health status logging raised exception: {e}")
    
    def test_health_check_performance(self):
        """Test health check performance and timing."""
        start_time = time.time()
        health_status = CacheHealthMonitor.check_cache_backend_health()
        end_time = time.time()
        
        health_check_time = end_time - start_time
        
        # Health check should complete within reasonable time
        self.assertLess(health_check_time, 2.0,
                       f"Health check should complete within 2 seconds, "
                       f"took {health_check_time:.3f}s")
        
        # Response time should be measured
        self.assertIsNotNone(health_status['response_time'],
                            "Response time should be measured")
        self.assertIsInstance(health_status['response_time'], float,
                             "Response time should be a float")


class CacheAlertSystemTestCase(TestCase):
    """
    Test CacheAlertSystem functionality.
    
    This test case verifies the cache alerting system properly monitors
    hit rates, page load times, and cache connectivity.
    """
    
    def setUp(self):
        """Clear cache and reset alert system before each test."""
        cache.clear()
        self.alert_system = CacheAlertSystem()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_hit_rate_check_passing(self):
        """Test hit rate check with passing threshold (80%)."""
        result = self.alert_system.check_hit_rate(80, 100)  # 80% hit rate
        self.assertTrue(result, "Hit rate check should pass for 80%")
    
    def test_hit_rate_check_failing(self):
        """Test hit rate check with failing threshold (60%)."""
        result = self.alert_system.check_hit_rate(60, 100)  # 60% hit rate
        self.assertFalse(result, "Hit rate check should fail for 60%")
    
    def test_page_load_time_check_first_measurement(self):
        """Test page load time check with first measurement."""
        result = self.alert_system.check_page_load_time(0.1)  # First measurement
        self.assertTrue(result, "First page load time should pass")
    
    def test_page_load_time_check_significant_increase(self):
        """Test page load time check with significant increase."""
        # First measurement
        self.alert_system.check_page_load_time(0.1)
        
        # Test significant increase (50% increase)
        result = self.alert_system.check_page_load_time(0.15)
        self.assertFalse(result, "Significant page load increase should fail")
    
    def test_cache_connectivity_check(self):
        """Test cache connectivity check."""
        result = self.alert_system.check_cache_connectivity()
        self.assertIsInstance(result, bool,
                             "Connectivity check should return boolean")
    
    def test_alert_threshold_values(self):
        """Test specific alert threshold values."""
        # Verify threshold values match requirements
        self.assertEqual(self.alert_system.hit_rate_threshold, 0.70,
                        "Hit rate threshold should be 70%")
        self.assertEqual(self.alert_system.response_time_threshold, 0.5,
                        "Response time threshold should be 500ms")
        self.assertEqual(self.alert_system.page_load_increase_threshold, 0.20,
                        "Page load increase threshold should be 20%")


class CacheMonitoringMiddlewareTestCase(TestCase):
    """
    Test CacheMonitoringMiddleware functionality.
    
    This test case verifies the middleware properly monitors cache operations
    during request/response cycles.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        cache.clear()
        self.factory = RequestFactory()
        
        # Create middleware instance with mock get_response
        def mock_get_response(request):
            response = MagicMock()
            response.status_code = 200
            return response
        
        self.middleware = CacheMonitoringMiddleware(mock_get_response)
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_process_request(self):
        """Test middleware process_request functionality."""
        request = self.factory.get('/')
        
        result = self.middleware.process_request(request)
        
        self.assertIsNone(result, "process_request should return None")
        self.assertTrue(hasattr(request, '_cache_start_time'),
                       "Request should have cache start time")
        self.assertTrue(hasattr(request, '_cache_operations'),
                       "Request should have cache operations list")
    
    def test_process_response(self):
        """Test middleware process_response functionality."""
        request = self.factory.get('/')
        response = MagicMock()
        response.status_code = 200
        
        # Initialize request attributes
        self.middleware.process_request(request)
        
        # Add some test operations
        request._cache_operations = [0.05, 0.15, 0.02]  # Mix of fast and slow operations
        
        result = self.middleware.process_response(request, response)
        
        self.assertEqual(result, response,
                        "process_response should return the response")
    
    def test_middleware_with_cache_operations(self):
        """Test middleware tracking of cache operations."""
        request = self.factory.get('/')
        
        # Initialize request
        self.middleware.process_request(request)
        
        # Verify cache operations list is initialized
        self.assertIsInstance(request._cache_operations, list,
                             "Cache operations should be a list")
        self.assertEqual(len(request._cache_operations), 0,
                        "Cache operations list should start empty")


class CacheOperationsMonitoringTestCase(TestCase):
    """
    Test cache operations with monitoring wrappers.
    
    This test case verifies cache operations work correctly while
    being monitored for performance metrics.
    """
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_cache_set_and_get_with_monitoring(self):
        """Test cache set and get operations with monitoring."""
        test_key = 'test_monitoring_key'
        test_value = 'test_monitoring_value'
        
        # Set a value
        cache.set(test_key, test_value, 300)
        
        # Get the value
        retrieved_value = cache.get(test_key)
        self.assertEqual(retrieved_value, test_value,
                        "Retrieved value should match set value")
    
    def test_cache_miss_with_monitoring(self):
        """Test cache miss behavior with monitoring."""
        missing_value = cache.get('non_existent_key', 'default')
        self.assertEqual(missing_value, 'default',
                        "Should return default for missing key")
    
    def test_cache_delete_with_monitoring(self):
        """Test cache delete operation with monitoring."""
        test_key = 'test_monitoring_key'
        test_value = 'test_monitoring_value'
        
        # Set a value
        cache.set(test_key, test_value, 300)
        
        # Delete the value
        cache.delete(test_key)
        
        # Verify deletion
        deleted_value = cache.get(test_key, 'not_found')
        self.assertEqual(deleted_value, 'not_found',
                        "Key should be deleted")
