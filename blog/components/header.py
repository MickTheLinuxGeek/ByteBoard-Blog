"""Header component for the Byte Board Blog."""

from reactpy import component, html


@component
def Header():
    """Header component that displays the blog title and navigation links."""
    return html.header(
        {"class": "bg-dark text-white py-3"},
        html.div(
            {"class": "container"},
            html.div(
                {"class": "row"},
                html.div(
                    {"class": "col-md-8"},
                    html.h1(
                        html.a(
                            {
                                "href": "/",
                                "class": "text-white text-decoration-none",
                            },
                            "Byte Board Blog",
                        ),
                    ),
                ),
                html.div(
                    {"class": "col-md-4 d-flex align-items-center justify-content-end"},
                    html.a(
                        {
                            "href": "/reactpy-demo/",
                            "class": "text-white me-3",
                        },
                        "ReactPy Demo",
                    ),
                    html.a(
                        {
                            "href": "/rss/",
                            "class": "text-white me-3",
                        },
                        "RSS",
                    ),
                    html.a(
                        {
                            "href": "/atom/",
                            "class": "text-white",
                        },
                        "Atom",
                    ),
                ),
            ),
        ),
    )
