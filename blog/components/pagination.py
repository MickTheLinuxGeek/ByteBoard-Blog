"""Pagination component for the Byte Board Blog."""

from reactpy import component, html


@component
def Pagination(page_obj=None, query_params=None):
    """
    Component for displaying pagination controls.

    Args:
        page_obj: Pagination object with page, paginator, has_next, has_previous attributes
        query_params: Dictionary of query parameters to preserve in pagination links

    """
    if page_obj is None or not hasattr(page_obj, "paginator"):
        return None

    # Helper function to build URLs with preserved query parameters
    def build_url(page_num):
        if query_params:
            params = query_params.copy()
            params['page'] = page_num
            query_string = '&'.join(f"{k}={v}" for k, v in params.items() if v)
            return f"?{query_string}"
        return f"?page={page_num}"

    # Generate page range to display
    paginator = page_obj.paginator
    current_page = page_obj.number

    # Always show first, last, current, and 2 pages on either side of current
    page_range = []  # Research this issue and fix later

    # Add first page
    page_range.append(1)

    # Add ellipsis if needed
    if current_page - 2 > 2:  # noqa: PLR2004
        page_range.append("...")

    # Add pages around current page
    for i in range(
        max(2, current_page - 2),
        min(paginator.num_pages, current_page + 3),
    ):
        page_range.append(i)  # noqa: PERF402

    # Add ellipsis if needed
    if current_page + 2 < paginator.num_pages - 1:
        page_range.append("...")

    # Add last page if it's not already included
    if paginator.num_pages > 1 and paginator.num_pages not in page_range:
        page_range.append(paginator.num_pages)

    return html.nav(
        {"aria-label": "Page navigation"},
        html.ul(
            {"class": "pagination justify-content-center"},
            # Previous button
            html.li(
                {
                    "class": f"page-item {'disabled' if not page_obj.has_previous() else ''}",
                },
                html.a(
                    {
                        "class": "page-link",
                        "href": build_url(page_obj.previous_page_number())
                        if page_obj.has_previous()
                        else "#",
                        "aria-label": "Previous",
                    },
                    html.span({"aria-hidden": "true"}, "«"),
                ),
            ),
            # Page numbers
            [
                html.li(
                    {
                        "class": f"page-item {'active' if page == current_page else ''} {'disabled' if page == '...' else ''}",
                    },
                    html.a(
                        {
                            "class": "page-link",
                            "href": build_url(page)
                            if page not in ("...", current_page)
                            else "#",
                        },
                        str(page),
                    ),
                )
                for page in page_range
            ],
            # Next button
            html.li(
                {
                    "class": f"page-item {'disabled' if not page_obj.has_next() else ''}",
                },
                html.a(
                    {
                        "class": "page-link",
                        "href": build_url(page_obj.next_page_number())
                        if page_obj.has_next()
                        else "#",
                        "aria-label": "Next",
                    },
                    html.span({"aria-hidden": "true"}, "»"),
                ),
            ),
        ),
    )
