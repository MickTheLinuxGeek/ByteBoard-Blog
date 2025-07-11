"""SearchBar component for the Byte Board Blog."""

from reactpy import component, hooks, html


@component
def SearchBar(placeholder="Search posts...", action="/search/"):
    """
    Component for displaying a search bar.

    Args:
        placeholder: Placeholder text for the search input
        action: Form action URL

    """
    # State for the search query
    query, set_query = hooks.use_state("")

    # Handle input change
    def handle_change(event):
        set_query(event["target"]["value"])

    return html.div(
        {"class": "card mb-4"},
        html.div({"class": "card-header"}, "Search"),
        html.div(
            {"class": "card-body"},
            html.form(
                {
                    "action": action,
                    "method": "get",
                    "class": "d-flex",
                },
                html.input(
                    {
                        "type": "text",
                        "name": "q",
                        "class": "form-control me-2",
                        "placeholder": placeholder,
                        "value": query,
                        "on_change": handle_change,
                        "aria-label": "Search",
                    },
                ),
                html.button(
                    {
                        "type": "submit",
                        "class": "btn btn-outline-primary",
                    },
                    "Search",
                ),
            ),
        ),
    )
