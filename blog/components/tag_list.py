"""TagList component for the Byte Board Blog."""

from reactpy import component, html


@component
def TagList(tags=None, title="Tags"):
    """
    Component for displaying a list of tags.

    Args:
        tags: List of Tag objects with name and slug attributes
        title: Title to display above the tag list

    """
    if tags is None:
        tags = []

    return html.div(
        {"class": "card mb-4"},
        html.div({"class": "card-header"}, title),
        html.div(
            {"class": "card-body"},
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
                    for tag in tags
                ]
                if tags
                else [html.p("No tags available.")],
            ),
        ),
    )
