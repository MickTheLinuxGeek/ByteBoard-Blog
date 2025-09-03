from .models import Category, Tag


def blog_context(request):
    """
    Provides global context for the blog, such as categories and tags for the sidebar.
    """
    return {
        "all_categories": Category.objects.all(),
        "all_tags": Tag.objects.all(),
        # You can add your archive dates logic here as well
        # 'archive_dates': ...
    }
