"""PostList component for the Byte Board Blog."""

from reactpy import component, html

from .pagination import Pagination
from .post_list_item import PostListItem


@component
def PostList(posts=None, page_obj=None, title="Latest Posts"):
    """
    Component for displaying a list of posts with pagination.

    Args:
        posts: List of Post objects
        page_obj: Pagination object with page, paginator, has_next, has_previous attributes
        title: Title to display above the post list

    """
    if posts is None:
        posts = []

    return html.div(
        html.h1({"class": "mb-4"}, title),
        # Display posts if available
        [PostListItem(post_id=post.id) for post in posts]
        if posts
        else html.div({"class": "alert alert-info"}, "No posts available."),
        # Display pagination if page_obj is provided
        Pagination(page_obj=page_obj) if page_obj else None,
    )
