"""PostListItem component for the Byte Board Blog."""

from asgiref.sync import sync_to_async
from reactpy import component, html
from reactpy_django.hooks import use_query

from blog.models import Post


# --- Helper ---
def _truncate_content(content, max_length=200):
    if len(content) <= max_length:
        return content
    truncated = content[:max_length]
    last_space = truncated.rfind(" ")
    if last_space != -1:
        truncated = truncated[:last_space]
    return truncated + "..."


@sync_to_async
def fetch_post(*, post_id):
    return (
        Post.objects.select_related("author")
        .prefetch_related("categories", "tags")
        .get(id=post_id)
    )


# --- MAIN PostListItem Component ---
@component
def PostListItem(post_id: int):
    post_query = use_query(
        fetch_post,
        {"post_id": post_id},
    )

    if post_query.loading:
        return html.div("Loading post...")

    if post_query.error:
        return html.div(f"Error loading post: {post_query.error}")

    if post_query.error or not post_query.data:
        return html.div("Error loading post.")

    post = post_query.data

    return html.div(
        {"class": "card mb-4"},
        html.div(
            {"class": "card-header"},
            html.h2(
                html.a(
                    {"href": f"/post/{post.slug}/", "class": "text-decoration-none"},
                    post.title,
                ),
            ),
            html.div(
                {"class": "text-muted small"},
                f"Published on {post.published_date.strftime('%B %d, %Y')} by {post.author.username}",
            ),
        ),
        html.div(
            {"class": "card-body"},
            html.div({"class": "card-text"}, _truncate_content(post.content, 200)),
            html.div(
                {"class": "mt-3"},
                html.a(
                    {"href": f"/post/{post.slug}/", "class": "btn btn-primary btn-sm"},
                    "Read More",
                ),
            ),
        ),
        html.div(
            {"class": "card-footer text-muted"},
            html.div(
                {"class": "d-flex justify-content-between align-items-center"},
                html.div(
                    {"class": "small"},
                    "Categories: ",
                    [
                        html.a(
                            {
                                "href": f"/category/{cat.slug}/",
                                "class": "badge bg-primary text-decoration-none me-1",
                            },
                            cat.name,
                        )
                        for cat in post.categories.all()
                    ]
                    or [html.span({"class": "list-inline-item"}, "None")],
                ),
                html.div(
                    {"class": "small"},
                    "Tags: ",
                    [
                        html.a(
                            {
                                "href": f"/tag/{tag.slug}/",
                                "class": "badge bg-secondary text-decoration-none me-1",
                            },
                            tag.name,
                        )
                        for tag in post.tags.all()
                    ]
                    or [html.span("None")],
                ),
            ),
        ),
    )
