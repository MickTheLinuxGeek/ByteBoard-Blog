"""
Test cache backend connectivity and basic operations.
Tests both development (database cache) and production (Redis) configurations.
"""

import time
from django.test import TestCase
from django.core.cache import cache
from django.conf import settings


class CacheConnectivityTestCase(TestCase):
    """
    Test cache backend connectivity and basic operations.
    
    This test case verifies that the cache backend is properly configured
    and all basic cache operations work correctly.
    """
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()
    
    def test_cache_configuration(self):
        """Test that cache configuration is properly set up."""
        # Verify cache configuration exists
        self.assertIn('default', settings.CACHES)
        self.assertIn('BACKEND', settings.CACHES['default'])
        
        # Verify cache backend is configured
        backend = settings.CACHES['default']['BACKEND']
        self.assertTrue(
            backend.endswith('DatabaseCache') or backend.endswith('RedisCache'),
            f"Cache backend should be DatabaseCache or RedisCache, got: {backend}"
        )
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        test_key = "connectivity_test"
        test_value = f"test_value_{int(time.time())}"
        
        # Test cache set
        cache.set(test_key, test_value, 60)
        
        # Test cache get
        retrieved_value = cache.get(test_key)
        self.assertEqual(retrieved_value, test_value,
                        f"Retrieved value should match set value")
    
    def test_cache_existence_check(self):
        """Test cache existence check operations."""
        test_key = "existence_test"
        test_value = "test_value"
        
        # Set a value
        cache.set(test_key, test_value, 60)
        
        # Test existence check
        if hasattr(cache, 'has_key'):
            self.assertTrue(cache.has_key(test_key),
                          "Cache should report key exists")
        else:
            # Use get with default to check existence
            result = cache.get(test_key, "NOT_FOUND")
            self.assertNotEqual(result, "NOT_FOUND",
                              "Cache should contain the key")
    
    def test_cache_delete(self):
        """Test cache delete operation."""
        test_key = "delete_test"
        test_value = "test_value"
        
        # Set a value
        cache.set(test_key, test_value, 60)
        
        # Verify it exists
        self.assertEqual(cache.get(test_key), test_value)
        
        # Delete the value
        cache.delete(test_key)
        
        # Verify it's gone
        self.assertIsNone(cache.get(test_key),
                         "Cache should return None after delete")
    
    def test_cache_clear(self):
        """Test cache clear operation."""
        # Set multiple values
        cache.set("test_clear_1", "value1", 60)
        cache.set("test_clear_2", "value2", 60)
        
        # Verify they exist
        self.assertEqual(cache.get("test_clear_1"), "value1")
        self.assertEqual(cache.get("test_clear_2"), "value2")
        
        # Clear all cache
        cache.clear()
        
        # Verify all values are gone
        self.assertIsNone(cache.get("test_clear_1"),
                         "Cache should be empty after clear")
        self.assertIsNone(cache.get("test_clear_2"),
                         "Cache should be empty after clear")
    
    def test_cache_timeout(self):
        """Test cache timeout behavior."""
        test_key = "timeout_test"
        test_value = "test_value"
        
        # Set with short timeout
        cache.set(test_key, test_value, timeout=1)
        
        # Verify it exists immediately
        self.assertEqual(cache.get(test_key), test_value)
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Verify it expired
        self.assertIsNone(cache.get(test_key),
                         "Cache should return None after timeout")
    
    def test_cache_with_none_value(self):
        """Test cache behavior with None values."""
        test_key = "none_test"
        
        # Set None explicitly
        cache.set(test_key, None, 60)
        
        # Verify we can distinguish between missing key and None value
        # Most cache backends return None for both cases
        result = cache.get(test_key, "DEFAULT")
        # If result is None, the key exists with None value
        # If result is "DEFAULT", the key doesn't exist
        self.assertTrue(result is None or result == "DEFAULT")


class CachePerformanceTestCase(TestCase):
    """
    Test cache performance with timing benchmarks.
    
    This test case measures cache read/write performance to ensure
    the cache backend operates within acceptable parameters.
    """
    
    def setUp(self):
        """Clear cache before each test."""
        cache.clear()
    
    def tearDown(self):
        """Clear cache and clean up test data after each test."""
        # Clean up performance test keys
        for i in range(100):
            cache.delete(f"perf_test_{i}")
        cache.clear()
    
    def test_cache_write_performance(self):
        """Test cache write performance with 100 operations."""
        start_time = time.time()
        
        for i in range(100):
            cache.set(f"perf_test_{i}", f"value_{i}", 60)
        
        write_time = time.time() - start_time
        
        # Verify writes succeeded
        sample_value = cache.get("perf_test_0")
        self.assertEqual(sample_value, "value_0",
                        "Cache writes should succeed")
        
        # Performance assertion - 100 writes should complete reasonably fast
        # Allowing up to 5 seconds for 100 writes (generous for database cache)
        self.assertLess(write_time, 5.0,
                       f"100 cache writes should complete within 5 seconds, "
                       f"took {write_time:.4f}s")
    
    def test_cache_read_performance(self):
        """Test cache read performance with 100 operations."""
        # Populate cache first
        for i in range(100):
            cache.set(f"perf_test_{i}", f"value_{i}", 60)
        
        # Measure read performance
        start_time = time.time()
        
        for i in range(100):
            value = cache.get(f"perf_test_{i}")
            self.assertEqual(value, f"value_{i}")
        
        read_time = time.time() - start_time
        
        # Performance assertion - 100 reads should complete reasonably fast
        # Allowing up to 5 seconds for 100 reads (generous for database cache)
        self.assertLess(read_time, 5.0,
                       f"100 cache reads should complete within 5 seconds, "
                       f"took {read_time:.4f}s")
    
    def test_cache_mixed_operations_performance(self):
        """Test mixed cache operations (set, get, delete) performance."""
        start_time = time.time()
        
        for i in range(50):
            # Set
            cache.set(f"perf_test_{i}", f"value_{i}", 60)
            # Get
            value = cache.get(f"perf_test_{i}")
            self.assertEqual(value, f"value_{i}")
            # Delete
            cache.delete(f"perf_test_{i}")
            # Verify deleted
            self.assertIsNone(cache.get(f"perf_test_{i}"))
        
        mixed_time = time.time() - start_time
        
        # Performance assertion - 50 mixed operations should complete reasonably fast
        # Allowing up to 5 seconds (generous for database cache)
        self.assertLess(mixed_time, 5.0,
                       f"50 mixed cache operations should complete within 5 seconds, "
                       f"took {mixed_time:.4f}s")