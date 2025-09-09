"""
Cache monitoring middleware for tracking cache performance metrics.
"""

import time
import logging
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger('blog.cache')
health_logger = logging.getLogger('blog.cache.health')


class CacheHealthMonitor:
    """
    Cache backend health monitoring utilities.
    """
    
    @staticmethod
    def check_cache_backend_health():
        """
        Perform health checks on the cache backend.
        
        Returns:
            dict: Health check results with status and metrics
        """
        health_status = {
            'healthy': True,
            'backend': 'unknown',
            'connectivity': True,
            'response_time': None,
            'errors': []
        }
        
        try:
            # Test basic connectivity with a health check key
            health_check_key = 'cache_health_check'
            test_value = f'health_check_{int(time.time())}'
            
            # Measure response time for SET operation
            start_time = time.time()
            cache.set(health_check_key, test_value, 60)  # 1 minute TTL
            set_time = time.time() - start_time
            
            # Measure response time for GET operation
            start_time = time.time()
            retrieved_value = cache.get(health_check_key)
            get_time = time.time() - start_time
            
            # Calculate total response time
            total_response_time = set_time + get_time
            health_status['response_time'] = total_response_time
            
            # Check if the value was stored and retrieved correctly
            if retrieved_value != test_value:
                health_status['healthy'] = False
                health_status['connectivity'] = False
                health_status['errors'].append('Cache data integrity check failed')
            
            # Check response time thresholds
            if total_response_time > 0.5:  # 500ms threshold
                health_status['healthy'] = False
                health_status['errors'].append(f'High response time: {total_response_time:.3f}s')
            elif total_response_time > 0.2:  # 200ms warning
                health_logger.warning(f'Cache response time elevated: {total_response_time:.3f}s')
            
            # Clean up test key
            cache.delete(health_check_key)
            
            # Try to determine backend type
            try:
                backend_class = cache.__class__.__name__
                health_status['backend'] = backend_class
            except AttributeError:
                health_status['backend'] = 'unknown'
            
        except Exception as e:
            health_status['healthy'] = False
            health_status['connectivity'] = False
            health_status['errors'].append(f'Cache backend error: {str(e)}')
            health_logger.error(f'Cache health check failed: {str(e)}')
        
        return health_status
    
    @staticmethod
    def log_health_status(health_status):
        """Log cache health status."""
        if health_status['healthy']:
            health_logger.info(
                f"Cache backend healthy - Backend: {health_status['backend']}, "
                f"Response time: {health_status['response_time']:.3f}s"
            )
        else:
            health_logger.error(
                f"Cache backend unhealthy - Backend: {health_status['backend']}, "
                f"Errors: {', '.join(health_status['errors'])}"
            )


class CacheAlertSystem:
    """
    Cache performance alerting system.
    """
    
    def __init__(self):
        self.hit_rate_threshold = 0.70  # 70% minimum hit rate
        self.response_time_threshold = 0.5  # 500ms maximum response time
        self.page_load_increase_threshold = 0.20  # 20% maximum increase
        self.last_page_load_time = None
        
    def check_hit_rate(self, hits, total_operations):
        """Check if cache hit rate is below threshold."""
        if total_operations > 0:
            hit_rate = hits / total_operations
            if hit_rate < self.hit_rate_threshold:
                health_logger.error(
                    f"ALERT: Cache hit rate below threshold - "
                    f"Current: {hit_rate:.2%}, Threshold: {self.hit_rate_threshold:.2%}"
                )
                return False
        return True
    
    def check_page_load_time(self, current_load_time):
        """Check if page load time increased significantly."""
        if self.last_page_load_time is not None:
            increase_ratio = (current_load_time - self.last_page_load_time) / self.last_page_load_time
            if increase_ratio > self.page_load_increase_threshold:
                health_logger.error(
                    f"ALERT: Page load time increased significantly - "
                    f"Previous: {self.last_page_load_time:.3f}s, "
                    f"Current: {current_load_time:.3f}s, "
                    f"Increase: {increase_ratio:.2%}"
                )
                return False
        
        self.last_page_load_time = current_load_time
        return True
    
    def check_cache_connectivity(self):
        """Check cache backend connectivity and alert on issues."""
        health_status = CacheHealthMonitor.check_cache_backend_health()
        
        if not health_status['healthy']:
            health_logger.error(
                f"ALERT: Cache backend connectivity issues - "
                f"Errors: {', '.join(health_status['errors'])}"
            )
            return False
        
        # Alert on elevated response times
        if health_status['response_time'] and health_status['response_time'] > self.response_time_threshold:
            health_logger.warning(
                f"ALERT: Cache response time elevated - "
                f"Current: {health_status['response_time']:.3f}s, "
                f"Threshold: {self.response_time_threshold:.3f}s"
            )
        
        return True


class CacheMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor cache operations and collect performance metrics.
    
    Tracks:
    - Cache hit/miss ratios
    - Cache operation timing
    - Slow cache operations (>100ms)
    - Cache backend health
    - Performance alerts
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.cache_hits = 0
        self.cache_misses = 0
        self.slow_operations = 0
        self.alert_system = CacheAlertSystem()
        self.request_count = 0
        self.health_check_interval = 100  # Check health every 100 requests
        
    def process_request(self, request):
        """Start timing cache operations for this request."""
        request._cache_start_time = time.time()
        request._cache_operations = []
        return None
        
    def process_response(self, request, response):
        """Log cache metrics and run performance alerts for this request."""
        if hasattr(request, '_cache_start_time'):
            total_time = time.time() - request._cache_start_time
            self.request_count += 1
            
            # Log cache operations if there were any
            if hasattr(request, '_cache_operations') and request._cache_operations:
                cache_ops = len(request._cache_operations)
                slow_ops = sum(1 for op_time in request._cache_operations if op_time > 0.1)
                
                if slow_ops > 0:
                    logger.warning(
                        f"Slow cache operations detected: {slow_ops} operations > 100ms "
                        f"in request to {request.path}"
                    )
                
                # Log cache statistics periodically
                if cache_ops > 0:
                    logger.debug(
                        f"Cache operations for {request.path}: {cache_ops} ops, "
                        f"total time: {total_time:.3f}s"
                    )
            
            # Run performance alerts
            self._run_performance_alerts(total_time)
            
            # Run periodic health checks
            if self.request_count % self.health_check_interval == 0:
                self.alert_system.check_cache_connectivity()
        
        return response
    
    def _run_performance_alerts(self, page_load_time):
        """Run performance alert checks."""
        try:
            # Check hit rate if we have enough data
            total_ops = self.cache_hits + self.cache_misses
            if total_ops >= 10:  # Only check after at least 10 operations
                self.alert_system.check_hit_rate(self.cache_hits, total_ops)
            
            # Check page load time trends
            self.alert_system.check_page_load_time(page_load_time)
            
        except Exception as e:
            health_logger.error(f"Error running performance alerts: {str(e)}")


def monitored_cache_get(original_get):
    """Wrapper for cache.get to monitor hit/miss ratios and timing."""
    def wrapper(key, default=None, version=None):
        start_time = time.time()
        result = original_get(key, default, version)
        operation_time = time.time() - start_time
        
        # Log slow operations
        if operation_time > 0.1:  # 100ms threshold
            logger.warning(
                f"Slow cache GET operation: {operation_time:.3f}s for key '{key}'"
            )
        
        # Track hit/miss
        if result is default:
            logger.debug(f"Cache MISS for key: {key}")
        else:
            logger.debug(f"Cache HIT for key: {key}")
            
        return result
    return wrapper


def monitored_cache_set(original_set):
    """Wrapper for cache.set to monitor timing."""
    def wrapper(key, value, timeout=DEFAULT_TIMEOUT, version=None):
        start_time = time.time()
        result = original_set(key, value, timeout, version)
        operation_time = time.time() - start_time
        
        # Log slow operations
        if operation_time > 0.1:  # 100ms threshold
            logger.warning(
                f"Slow cache SET operation: {operation_time:.3f}s for key '{key}'"
            )
        
        logger.debug(f"Cache SET for key: {key}, timeout: {timeout}")
        return result
    return wrapper


def monitored_cache_delete(original_delete):
    """Wrapper for cache.delete to monitor timing."""
    def wrapper(key, version=None):
        start_time = time.time()
        result = original_delete(key, version)
        operation_time = time.time() - start_time
        
        # Log slow operations
        if operation_time > 0.1:  # 100ms threshold
            logger.warning(
                f"Slow cache DELETE operation: {operation_time:.3f}s for key '{key}'"
            )
        
        logger.debug(f"Cache DELETE for key: {key}")
        return result
    return wrapper


# Monkey patch cache methods to add monitoring
cache.get = monitored_cache_get(cache.get)
cache.set = monitored_cache_set(cache.set)
cache.delete = monitored_cache_delete(cache.delete)