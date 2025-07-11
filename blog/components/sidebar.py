"""Sidebar component for the Byte Board Blog."""

from reactpy import component, html

from .category_list import CategoryList
from .search_bar import SearchBar
from .tag_list import TagList


@component
def Sidebar(categories=None, tags=None, archive_dates=None):
    """
    Sidebar component that displays categories, tags, and archives.

    Args:
        categories: List of category objects with name and slug attributes
        tags: List of tag objects with name and slug attributes
        archive_dates: List of dictionaries with year and months attributes

    """
    if categories is None:
        categories = []
    if tags is None:
        tags = []
    if archive_dates is None:
        archive_dates = []

    return html.div(
        {"classname": "col-md-4"},
        # Search section
        SearchBar(),
        # Categories section
        CategoryList(categories=categories, title="Categories"),
        # Tags section
        TagList(tags=tags, title="Tags"),
        # Archives section
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
    return month_names[month_number - 1]
