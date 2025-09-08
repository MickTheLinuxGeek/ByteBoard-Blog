#!/usr/bin/env python
"""
Test script to verify cache backend connectivity.
Tests both development (database cache) and production (Redis) configurations.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'byte_board_blog.settings')
django.setup()

from django.core.cache import cache
from django.conf import settings
import time


def test_cache_connectivity():
    """Test cache backend connectivity and basic operations."""
    print("="*60)
    print("CACHE BACKEND CONNECTIVITY TEST")
    print("="*60)
    
    # Display current cache configuration
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Cache Backend: {settings.CACHES['default']['BACKEND']}")
    if 'LOCATION' in settings.CACHES['default']:
        print(f"Cache Location: {settings.CACHES['default']['LOCATION']}")
    print(f"Cache Key Prefix: {settings.CACHES['default'].get('KEY_PREFIX', 'None')}")
    print(f"Cache Timeout: {settings.CACHES['default'].get('TIMEOUT', 'Default')}")
    print("-"*60)
    
    # Test basic cache operations
    test_key = "connectivity_test"
    test_value = f"test_value_{int(time.time())}"
    
    try:
        print("Testing cache operations...")
        
        # Test cache set
        print("1. Testing cache.set()...")
        cache.set(test_key, test_value, 60)
        print("   ✓ cache.set() successful")
        
        # Test cache get
        print("2. Testing cache.get()...")
        retrieved_value = cache.get(test_key)
        if retrieved_value == test_value:
            print("   ✓ cache.get() successful - value matches")
        else:
            print(f"   ✗ cache.get() failed - expected '{test_value}', got '{retrieved_value}'")
            return False
            
        # Test cache has_key (if available)
        print("3. Testing cache existence check...")
        if hasattr(cache, 'has_key'):
            if cache.has_key(test_key):
                print("   ✓ cache.has_key() successful")
            else:
                print("   ✗ cache.has_key() failed")
                return False
        else:
            # Use get with default to check existence
            if cache.get(test_key, "NOT_FOUND") != "NOT_FOUND":
                print("   ✓ cache existence check successful")
            else:
                print("   ✗ cache existence check failed")
                return False
        
        # Test cache delete
        print("4. Testing cache.delete()...")
        cache.delete(test_key)
        if cache.get(test_key) is None:
            print("   ✓ cache.delete() successful")
        else:
            print("   ✗ cache.delete() failed")
            return False
            
        # Test cache clear (be careful with this in production!)
        print("5. Testing cache.clear() (creates test data first)...")
        cache.set("test_clear_1", "value1", 60)
        cache.set("test_clear_2", "value2", 60)
        cache.clear()
        if cache.get("test_clear_1") is None and cache.get("test_clear_2") is None:
            print("   ✓ cache.clear() successful")
        else:
            print("   ✗ cache.clear() failed")
            return False
            
        print("-"*60)
        print("✓ ALL CACHE OPERATIONS SUCCESSFUL")
        print("✓ Cache backend is working properly")
        return True
        
    except Exception as e:
        print(f"✗ CACHE OPERATION FAILED: {str(e)}")
        print(f"✗ Cache backend connectivity issue detected")
        return False


def test_cache_performance():
    """Test cache performance with timing."""
    print("\n" + "="*60)
    print("CACHE PERFORMANCE TEST")
    print("="*60)
    
    try:
        # Test write performance
        print("Testing cache write performance...")
        start_time = time.time()
        for i in range(100):
            cache.set(f"perf_test_{i}", f"value_{i}", 60)
        write_time = time.time() - start_time
        print(f"   100 cache writes took: {write_time:.4f} seconds")
        
        # Test read performance
        print("Testing cache read performance...")
        start_time = time.time()
        for i in range(100):
            cache.get(f"perf_test_{i}")
        read_time = time.time() - start_time
        print(f"   100 cache reads took: {read_time:.4f} seconds")
        
        # Cleanup
        for i in range(100):
            cache.delete(f"perf_test_{i}")
            
        print("✓ Cache performance test completed")
        return True
        
    except Exception as e:
        print(f"✗ CACHE PERFORMANCE TEST FAILED: {str(e)}")
        return False


def main():
    """Main test function."""
    print("Starting cache backend connectivity tests...")
    print(f"Django version: {django.get_version()}")
    print(f"Python version: {sys.version}")
    
    # Run connectivity test
    connectivity_ok = test_cache_connectivity()
    
    # Run performance test only if connectivity is working
    if connectivity_ok:
        performance_ok = test_cache_performance()
    else:
        performance_ok = False
        
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Cache Connectivity: {'✓ PASS' if connectivity_ok else '✗ FAIL'}")
    print(f"Cache Performance: {'✓ PASS' if performance_ok else '✗ FAIL'}")
    
    if connectivity_ok and performance_ok:
        print("\n✓ ALL TESTS PASSED - Cache backend is working properly")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - Check cache configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())