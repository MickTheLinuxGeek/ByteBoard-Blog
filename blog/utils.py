"""
Caching utilities for the blog application.

This module provides cached versions of common context data to reduce
redundant database queries and improve performance.
"""

from django.core.cache import cache
from .models import Category, Post, Tag


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