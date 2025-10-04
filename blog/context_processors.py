from .utils import get_cached_common_context


def blog_context(request):
    """
    Provides global context for the blog, such as categories and tags for the sidebar.
    Uses cached data to improve performance.
    """
    context = get_cached_common_context()
    return {
        "all_categories": context["categories"],
        "all_tags": context["tags"],
        "archive_dates": context["archive_dates"],
    }
