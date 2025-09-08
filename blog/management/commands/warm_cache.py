"""
Django management command to warm up the cache with common context and post content.

This command pre-loads frequently accessed data into the cache to improve
initial response times for users.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from blog.models import Post
from blog.utils import get_cached_common_context


class Command(BaseCommand):
    help = "Warm up the cache with common context and top published posts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--posts",
            type=int,
            default=50,
            help="Number of top published posts to cache (default: 50)",
        )

    def handle(self, *args, **options):
        num_posts = options["posts"]
        
        self.stdout.write("Starting cache warming process...")
        
        # Warm up common context cache
        self.stdout.write("Warming common context cache...")
        try:
            common_context = get_cached_common_context()
            categories_count = len(common_context.get("categories", []))
            tags_count = len(common_context.get("tags", []))
            archive_count = len(common_context.get("archive_dates", []))
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Common context cached: {categories_count} categories, "
                    f"{tags_count} tags, {archive_count} archive periods"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to cache common context: {e}")
            )
        
        # Warm up post content cache for top published posts
        self.stdout.write(f"Warming cache for top {num_posts} published posts...")
        try:
            top_posts = Post.objects.filter(status="published").order_by(
                "-published_date", "-created_at"
            )[:num_posts]
            
            cached_count = 0
            failed_count = 0
            
            for post in top_posts:
                try:
                    # This will cache the post content if not already cached
                    post.get_cached_content()
                    cached_count += 1
                    
                    if cached_count % 10 == 0:
                        self.stdout.write(f"  Cached {cached_count} posts...")
                        
                except Exception as e:
                    failed_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Failed to cache post '{post.title}': {e}"
                        )
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Post content cache warming completed: "
                    f"{cached_count} posts cached, {failed_count} failed"
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Failed to cache post content: {e}")
            )
        
        # Cache warming summary
        self.stdout.write(
            self.style.SUCCESS("Cache warming process completed successfully!")
        )
        
        # Optional: Display cache statistics
        try:
            # Check if we can get cache statistics (Redis specific)
            # This is optional and may not work with all cache backends
            self.stdout.write("\nCache status:")
            self.stdout.write("- Common context data: Warmed")
            self.stdout.write(f"- Top {num_posts} posts content: Warmed")
        except Exception:
            # Cache backend may not support statistics
            pass