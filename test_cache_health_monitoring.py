#!/usr/bin/env python
"""
Test script for cache health monitoring functionality.
Tests cache health checks, alerting system, and monitoring middleware.
"""

import os
import sys
import time
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, '/home/mick/PycharmProjects/byte_board_blog')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byte_board_blog.settings')

import django
django.setup()

from django.core.cache import cache
from django.test import TestCase, RequestFactory
from blog.middleware import CacheHealthMonitor, CacheAlertSystem, CacheMonitoringMiddleware


def test_cache_health_monitor():
    """Test CacheHealthMonitor functionality."""
    print("Testing Cache Health Monitor...")
    
    # Test health check
    health_status = CacheHealthMonitor.check_cache_backend_health()
    
    print(f"Health Status: {health_status}")
    
    # Verify health status structure
    required_keys = ['healthy', 'backend', 'connectivity', 'response_time', 'errors']
    for key in required_keys:
        assert key in health_status, f"Missing key: {key}"
    
    # Test logging
    CacheHealthMonitor.log_health_status(health_status)
    
    print("✓ Cache Health Monitor tests passed")


def test_cache_alert_system():
    """Test CacheAlertSystem functionality."""
    print("Testing Cache Alert System...")
    
    alert_system = CacheAlertSystem()
    
    # Test hit rate check - should pass
    result = alert_system.check_hit_rate(80, 100)  # 80% hit rate
    assert result is True, "Hit rate check should pass for 80%"
    
    # Test hit rate check - should fail
    result = alert_system.check_hit_rate(60, 100)  # 60% hit rate
    assert result is False, "Hit rate check should fail for 60%"
    
    # Test page load time check
    result = alert_system.check_page_load_time(0.1)  # First measurement
    assert result is True, "First page load time should pass"
    
    # Test significant increase
    result = alert_system.check_page_load_time(0.15)  # 50% increase
    assert result is False, "Significant page load increase should fail"
    
    # Test connectivity check
    result = alert_system.check_cache_connectivity()
    print(f"Connectivity check result: {result}")
    
    print("✓ Cache Alert System tests passed")


def test_cache_monitoring_middleware():
    """Test CacheMonitoringMiddleware functionality."""
    print("Testing Cache Monitoring Middleware...")
    
    # Create middleware instance with mock get_response
    def mock_get_response(request):
        response = MagicMock()
        response.status_code = 200
        return response
    
    middleware = CacheMonitoringMiddleware(mock_get_response)
    
    # Create mock request and response
    factory = RequestFactory()
    request = factory.get('/')
    
    # Mock response
    response = MagicMock()
    response.status_code = 200
    
    # Test process_request
    result = middleware.process_request(request)
    assert result is None, "process_request should return None"
    assert hasattr(request, '_cache_start_time'), "Request should have cache start time"
    assert hasattr(request, '_cache_operations'), "Request should have cache operations list"
    
    # Add some test operations
    request._cache_operations = [0.05, 0.15, 0.02]  # Mix of fast and slow operations
    
    # Test process_response
    result = middleware.process_response(request, response)
    assert result == response, "process_response should return the response"
    
    print("✓ Cache Monitoring Middleware tests passed")


def test_cache_operations_with_monitoring():
    """Test cache operations with monitoring wrappers."""
    print("Testing Cache Operations with Monitoring...")
    
    # Test cache set and get operations
    test_key = 'test_monitoring_key'
    test_value = 'test_monitoring_value'
    
    # Set a value
    cache.set(test_key, test_value, 300)
    
    # Get the value
    retrieved_value = cache.get(test_key)
    assert retrieved_value == test_value, "Retrieved value should match set value"
    
    # Test cache miss
    missing_value = cache.get('non_existent_key', 'default')
    assert missing_value == 'default', "Should return default for missing key"
    
    # Test cache delete
    cache.delete(test_key)
    deleted_value = cache.get(test_key, 'not_found')
    assert deleted_value == 'not_found', "Key should be deleted"
    
    print("✓ Cache Operations with Monitoring tests passed")


def test_alert_thresholds():
    """Test specific alert threshold values."""
    print("Testing Alert Thresholds...")
    
    alert_system = CacheAlertSystem()
    
    # Verify threshold values match requirements
    assert alert_system.hit_rate_threshold == 0.70, "Hit rate threshold should be 70%"
    assert alert_system.response_time_threshold == 0.5, "Response time threshold should be 500ms"
    assert alert_system.page_load_increase_threshold == 0.20, "Page load increase threshold should be 20%"
    
    print("✓ Alert Thresholds tests passed")


def test_health_check_performance():
    """Test health check performance and timing."""
    print("Testing Health Check Performance...")
    
    start_time = time.time()
    health_status = CacheHealthMonitor.check_cache_backend_health()
    end_time = time.time()
    
    health_check_time = end_time - start_time
    print(f"Health check completed in {health_check_time:.3f}s")
    
    # Health check should complete within reasonable time
    assert health_check_time < 2.0, "Health check should complete within 2 seconds"
    
    # Response time should be measured
    assert health_status['response_time'] is not None, "Response time should be measured"
    assert isinstance(health_status['response_time'], float), "Response time should be a float"
    
    print("✓ Health Check Performance tests passed")


def run_all_tests():
    """Run all cache health monitoring tests."""
    print("=" * 60)
    print("CACHE HEALTH MONITORING TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_cache_health_monitor,
        test_cache_alert_system,
        test_cache_monitoring_middleware,
        test_cache_operations_with_monitoring,
        test_alert_thresholds,
        test_health_check_performance,
    ]
    
    for test_func in tests:
        try:
            test_func()
            print()
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed: {e}")
            return False
    
    print("=" * 60)
    print("✅ ALL CACHE HEALTH MONITORING TESTS PASSED!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)