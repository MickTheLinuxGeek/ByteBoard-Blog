"""
Caching utilities for the blog application.

This module provides cached versions of common context data to reduce
redundant database queries and improve performance.
"""

from functools import wraps
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from .models import Category, Post, Tag


def cache_for_anonymous_only(cache_decorator):
    """
    Custom decorator that applies caching only for anonymous users.
    Admin users will always see fresh content, bypassing the cache.
    
    Args:
        cache_decorator: The cache decorator to apply (e.g., cache_page(3600))
    
    Returns:
        Decorator function that conditionally applies caching
    """
    def decorator(view_func):
        # Apply never_cache for admin users
        never_cached_view = never_cache(view_func)
        # Apply the provided cache decorator for non-admin users
        cached_view = cache_decorator(view_func)
        
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated and is staff/admin
            if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
                # Admin users get fresh content (no cache)
                return never_cached_view(request, *args, **kwargs)
            else:
                # Anonymous or regular users get cached content
                return cached_view(request, *args, **kwargs)
        
        return wrapper
    return decorator


def _calculate_archive_dates():
    """
    Helper function to calculate archive dates (years and months with posts).
    
    Returns:
        list: List of dictionaries containing year and months data.
    """
    # Get archive dates (years and months with posts)
    published_dates = Post.objects.filter(status="published").dates(
        "published_date",
        "month",
        order="DESC",
    )

    archive_dates = []
    years_dict = {}

    for date in published_dates:
        year = date.year
        month = date.month

        if year not in years_dict:
            years_dict[year] = {"year": year, "months": []}

        if month not in years_dict[year]["months"]:
            years_dict[year]["months"].append(month)

    for year, data in sorted(years_dict.items(), reverse=True):
        archive_dates.append(
            {"year": year, "months": sorted(data["months"], reverse=True)},
        )

    return archive_dates


def get_cached_common_context():
    """
    Get common context data with caching to reduce database queries.
    
    Uses Django's cache framework with the following cache keys and TTL:
    - categories_all: 1 hour TTL (3600 seconds)
    - tags_all: 30 minutes TTL (1800 seconds)  
    - archive_dates: 6 hours TTL (21600 seconds)
    
    Returns:
        dict: Dictionary containing categories, tags, and archive_dates.
    """
    # Try to get cached data
    categories = cache.get("categories_all")
    tags = cache.get("tags_all")
    archive_dates = cache.get("archive_dates")
    
    # Fetch and cache categories if not in cache
    if categories is None:
        categories = list(Category.objects.all())
        cache.set("categories_all", categories, 3600)  # 1 hour TTL
    
    # Fetch and cache tags if not in cache
    if tags is None:
        tags = list(Tag.objects.all())
        cache.set("tags_all", tags, 1800)  # 30 minutes TTL
    
    # Fetch and cache archive dates if not in cache
    if archive_dates is None:
        archive_dates = _calculate_archive_dates()
        cache.set("archive_dates", archive_dates, 21600)  # 6 hours TTL
    
    return {
        "categories": categories,
        "tags": tags,
        "archive_dates": archive_dates,
    }