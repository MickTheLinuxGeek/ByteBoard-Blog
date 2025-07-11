"""Footer component for the Byte Board Blog."""

from datetime import datetime, timezone

from reactpy import component, html


@component
def Footer():
    """Footer component that displays copyright information."""
    current_year = datetime.now(
        tz=timezone.utc,
    ).year  # Fix this timezone argument; This will work for now

    return html.footer(
        {"class": "bg-dark text-white py-3 mt-4"},
        html.div(
            {"class": "container"},
            html.p(
                {"class": "m-0 text-center"},
                f"© {current_year} Michael Biel & Byte Board Blog.",
            ),
        ),
    )
