"""
Django management command for cache administration.

This command provides administrative tools for managing the application cache,
including clearing caches, displaying statistics, and pattern-based clearing.
"""

import re
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache, caches
from django.conf import settings


class Command(BaseCommand):
    help = "Administrative tools for cache management"

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['clear', 'stats', 'clear-pattern'],
            help='Action to perform: clear (all caches), stats (cache statistics), or clear-pattern (pattern-based clearing)'
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Pattern to match for selective cache clearing (required for clear-pattern action)'
        )
        parser.add_argument(
            '--cache',
            type=str,
            default='default',
            help='Cache alias to operate on (default: default)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleared without actually clearing (for clear-pattern action)'
        )

    def handle(self, *args, **options):
        action = options['action']
        cache_alias = options['cache']
        
        # Validate cache alias exists
        if cache_alias not in settings.CACHES:
            raise CommandError(f"Cache alias '{cache_alias}' not found in settings.")
        
        cache_backend = caches[cache_alias]
        
        if action == 'clear':
            self.handle_clear(cache_backend, cache_alias)
        elif action == 'stats':
            self.handle_stats(cache_backend, cache_alias)
        elif action == 'clear-pattern':
            pattern = options.get('pattern')
            if not pattern:
                raise CommandError("Pattern is required for clear-pattern action. Use --pattern option.")
            dry_run = options.get('dry_run', False)
            self.handle_clear_pattern(cache_backend, cache_alias, pattern, dry_run)

    def handle_clear(self, cache_backend, cache_alias):
        """Clear all caches."""
        self.stdout.write(f"Clearing all caches for '{cache_alias}' backend...")
        
        try:
            cache_backend.clear()
            self.stdout.write(
                self.style.SUCCESS(f"✓ All caches cleared for '{cache_alias}' backend")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to clear caches: {e}")
            )

    def handle_stats(self, cache_backend, cache_alias):
        """Display cache statistics."""
        self.stdout.write(f"Cache statistics for '{cache_alias}' backend:")
        self.stdout.write("=" * 50)
        
        try:
            # Basic cache backend information
            backend_class = cache_backend.__class__.__name__
            self.stdout.write(f"Backend Type: {backend_class}")
            
            # Try to get cache-specific statistics
            stats = self._get_cache_stats(cache_backend)
            
            if stats:
                for key, value in stats.items():
                    self.stdout.write(f"{key}: {value}")
            else:
                self.stdout.write("No detailed statistics available for this cache backend.")
                
            # Test cache connectivity
            test_key = "cache_admin_test"
            test_value = "test_value"
            
            try:
                cache_backend.set(test_key, test_value, 10)
                retrieved_value = cache_backend.get(test_key)
                cache_backend.delete(test_key)
                
                if retrieved_value == test_value:
                    self.stdout.write(
                        self.style.SUCCESS("✓ Cache connectivity: OK")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠ Cache connectivity: Issues detected")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Cache connectivity test failed: {e}")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to get cache statistics: {e}")
            )

    def handle_clear_pattern(self, cache_backend, cache_alias, pattern, dry_run):
        """Clear caches matching a specific pattern."""
        action_text = "Would clear" if dry_run else "Clearing"
        self.stdout.write(f"{action_text} cache keys matching pattern '{pattern}' for '{cache_alias}' backend...")
        
        try:
            # Get all cache keys (this method may vary by backend)
            keys_to_clear = self._get_matching_keys(cache_backend, pattern)
            
            if not keys_to_clear:
                self.stdout.write("No cache keys found matching the pattern.")
                return
                
            self.stdout.write(f"Found {len(keys_to_clear)} keys matching pattern:")
            for key in keys_to_clear:
                self.stdout.write(f"  - {key}")
            
            if not dry_run:
                cleared_count = 0
                failed_count = 0
                
                for key in keys_to_clear:
                    try:
                        cache_backend.delete(key)
                        cleared_count += 1
                    except Exception as e:
                        failed_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"  Failed to clear key '{key}': {e}")
                        )
                
                if cleared_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Successfully cleared {cleared_count} cache keys"
                        )
                    )
                if failed_count > 0:
                    self.stdout.write(
                        self.style.WARNING(f"⚠ Failed to clear {failed_count} cache keys")
                    )
            else:
                self.stdout.write("Dry run completed. Use without --dry-run to actually clear these keys.")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to clear cache pattern: {e}")
            )

    def _get_cache_stats(self, cache_backend):
        """Get cache-specific statistics if available."""
        stats = {}
        backend_class = cache_backend.__class__.__name__
        
        # For Redis cache backends
        if 'Redis' in backend_class:
            try:
                # Try to get Redis-specific stats
                if hasattr(cache_backend, '_cache'):
                    redis_client = cache_backend._cache.get_client()
                    info = redis_client.info()
                    stats.update({
                        'Total Keys': info.get('db0', {}).get('keys', 'N/A'),
                        'Memory Usage': f"{info.get('used_memory_human', 'N/A')}",
                        'Keyspace Hits': info.get('keyspace_hits', 'N/A'),
                        'Keyspace Misses': info.get('keyspace_misses', 'N/A'),
                    })
                    
                    # Calculate hit rate if available
                    hits = info.get('keyspace_hits', 0)
                    misses = info.get('keyspace_misses', 0)
                    if hits + misses > 0:
                        hit_rate = (hits / (hits + misses)) * 100
                        stats['Hit Rate'] = f"{hit_rate:.2f}%"
            except Exception:
                # Redis stats not available
                pass
        
        # For Database cache backends
        elif 'Database' in backend_class:
            try:
                # Try to get database cache table info
                stats['Cache Type'] = 'Database'
                # Could add more database-specific stats here
            except Exception:
                pass
        
        # For File cache backends
        elif 'File' in backend_class:
            try:
                stats['Cache Type'] = 'File System'
                # Could add file system cache stats here
            except Exception:
                pass
        
        return stats

    def _get_matching_keys(self, cache_backend, pattern):
        """Get cache keys matching the given pattern."""
        matching_keys = []
        backend_class = cache_backend.__class__.__name__
        
        # Compile regex pattern
        try:
            regex_pattern = re.compile(pattern)
        except re.error as e:
            raise CommandError(f"Invalid pattern: {e}")
        
        # For Redis cache backends
        if 'Redis' in backend_class:
            try:
                if hasattr(cache_backend, '_cache'):
                    redis_client = cache_backend._cache.get_client()
                    # Get all keys and filter by pattern
                    all_keys = redis_client.keys('*')
                    for key in all_keys:
                        key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                        if regex_pattern.search(key_str):
                            matching_keys.append(key_str)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Could not retrieve keys from Redis: {e}")
                )
        
        # For other backends, we have limited options
        else:
            # Common cache keys used in the application
            common_keys = [
                'categories_all',
                'tags_all', 
                'archive_dates',
                'categories_sidebar',
                'tags_sidebar',
                'archive_sidebar',
            ]
            
            # Add post-specific cache keys pattern
            from blog.models import Post
            try:
                published_posts = Post.objects.filter(status='published')
                for post in published_posts:
                    common_keys.extend([
                        f'post_content_{post.pk}',
                        f'post_summary_{post.pk}',
                        f'post_{post.pk}',
                    ])
            except Exception:
                pass
            
            # Filter common keys by pattern
            for key in common_keys:
                if regex_pattern.search(key):
                    # Check if key actually exists in cache
                    try:
                        if cache_backend.get(key) is not None or cache_backend.has_key(key):
                            matching_keys.append(key)
                    except Exception:
                        # If we can't check, include it anyway
                        matching_keys.append(key)
        
        return matching_keys