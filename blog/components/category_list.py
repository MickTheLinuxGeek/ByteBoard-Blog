"""CategoryList component for the Byte Board Blog."""

from reactpy import component, html


@component
def CategoryList(categories=None, title="Categories"):
    """
    Component for displaying a list of categories.

    Args:
        categories: List of Category objects with name and slug attributes
        title: Title to display above the category list

    """
    if categories is None:
        categories = []

    return html.div(
        {"class": "card mb-4"},
        html.div({"class": "card-header"}, title),
        html.div(
            {"class": "card-body"},
            html.ul(
                {"class": "list-unstyled"},
                [
                    html.li(
                        {"class": "mb-2"},
                        html.a(
                            {"href": f"/category/{category.slug}/"},
                            category.name,
                        ),
                    )
                    for category in categories
                ]
                if categories
                else [html.li("No categories available.")],
            ),
        ),
    )
