"""PostDetail component for the Byte Board Blog."""

from asgiref.sync import sync_to_async
from reactpy import component, html
from reactpy_django.hooks import use_query
from .content_markdown import Markdown
import pytz

from blog.models import Post


# --- Fetchers ---
@sync_to_async
def fetch_post_detail(*, post_id):
    return (
        Post.objects.select_related("author")
        .prefetch_related("categories", "tags")
        .get(id=post_id)
    )


# --- Component ---
@component
def PostDetail(post_id: int):
    # Main post
    post_query = use_query(
        fetch_post_detail,
        {"post_id": post_id},
    )

    # Handle loading or error states
    if post_query.loading:
        return html.div({"classname": "alert alert-info"}, "Loading post...")

    if post_query.error or not post_query.data:
        return html.div({"classname": "alert alert-warning"}, "Post not found.")

    post = post_query.data

    # Set timezone to local timezone instead of UTC
    local_tz = pytz.timezone("America/New_York")  # Change to your desired timezone
    local_time = post.published_date.astimezone(local_tz)
    formatted_date = local_time.strftime("%B %d, %Y")

    return html.div(
        {"class": "card mb-4"},
        # Post header
        html.div(
            {"class": "card-header"},
            html.h1({"class": "card-title text-info"}, post.title),
            html.div(
                {"class": "text-light"},
                f"Published on {formatted_date} by {post.author.username}",
            ),
        ),
        # Post content
        html.div(
            {"class": "card-body"},
            # html.div(
            Markdown(source=post.content),
            # {
            #     "dangerouslySetInnerHTML": {
            #         "__html": getattr(post, "content_html", post.content),
            #     },
            #     "class": "card-text markdown-content",
            # },
            # ),
        ),
        # Footer with categories and tags
        html.div(
            {"class": "card-footer"},
            html.div(
                {"class": "row"},
                # Categories
                html.div(
                    {"class": "col-md-6"},
                    html.h5("Categories:"),
                    html.ul(
                        {"class": "list-inline"},
                        [
                            html.li(
                                {"class": "list-inline-item"},
                                html.a(
                                    {
                                        "href": f"/category/{cat.slug}/",
                                        "class": "badge bg-primary text-decoration-none me-1",
                                    },
                                    cat.name,
                                ),
                            )
                            for cat in post.categories.all()
                        ]
                        or [html.li({"class": "list-inline-item"}, "None")],
                    ),
                ),
                # Tags
                html.div(
                    {"class": "col-md-6"},
                    html.h5("Tags:"),
                    html.div(
                        {"class": "d-flex flex-wrap gap-2"},
                        [
                            html.a(
                                {
                                    "href": f"/tag/{tag.slug}/",
                                    "class": "badge bg-secondary text-decoration-none",
                                },
                                tag.name,
                            )
                            for tag in post.tags.all()
                        ]
                        or [html.span("None")],
                    ),
                ),
            ),
            # # Back button
            # html.div(
            #     {"class": "mt-3"},
            #     html.a({"href": "/", "class": "btn btn-secondary"}, "Back to Posts"),
            # ),
        ),
    )
