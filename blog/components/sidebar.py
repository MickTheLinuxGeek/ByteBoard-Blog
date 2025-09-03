"""Sidebar component for the Byte Board Blog."""

from reactpy import component, html, use_state

from .category_list import CategoryList
from .search_bar import SearchBar
from .tag_list import TagList


@component
def Sidebar(categories=None, tags=None, archive_dates=None):
    show_sidebar, set_show_sidebar = use_state(False)

    if categories is None:
        categories = []
    if tags is None:
        tags = []
    if archive_dates is None:
        archive_dates = []

    return html.div(
        {"class": "sidebar-wrapper"},
        # Hamburger toggle button
        html.button(
            {
                "class": "hamburger-btn d-md-none",  # Hide on medium+ screens
                "on_click": lambda _: set_show_sidebar(not show_sidebar),
            },
            "☰ Menu",
        ),
        # Sidebar content
        html.div(
            {"class": f"sidebar-content {'show' if show_sidebar else 'hide'}"},
            SearchBar(),
            CategoryList(categories=categories, title="Categories"),
            TagList(tags=tags, title="Tags"),
            html.div(
                {"class": "card"},
                html.div({"class": "card-header"}, "Archives"),
                html.div(
                    {"class": "card-body"},
                    html.ul(
                        {"class": "list-unstyled"},
                        [
                            html.li(
                                [
                                    html.a(
                                        {"href": f"/archive/{date['year']}/"},
                                        str(date["year"]),
                                    ),
                                    html.ul(
                                        [
                                            html.li(
                                                html.a(
                                                    {
                                                        "href": f"/archive/{date['year']}/{month}/",
                                                    },
                                                    _get_month_name(month),
                                                ),
                                            )
                                            for month in date["months"]
                                        ],
                                    )
                                    if date.get("months")
                                    else None,
                                ],
                            )
                            for date in archive_dates
                        ]
                        if archive_dates
                        else [html.li("No archives yet.")],
                    ),
                ),
            ),
        ),
    )


def _get_month_name(month_number):
    """Helper function to convert month number to month name."""
    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    # Validate month number is in valid range (1-12)
    if not isinstance(month_number, int) or month_number < 1 or month_number > 12:
        raise IndexError(f"Month number must be between 1 and 12, got {month_number}")

    return month_names[month_number - 1]
