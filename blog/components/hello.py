"""A simple ReactPy component to test the integration with Django."""

from reactpy import component, html


@component
def helloworld():
    """A simple Hello World component."""
    return html.div(
        html.h1("Hello from ReactPy!"),
        html.p("This is a simple ReactPy component integrated with Django."),
        html.p("If you can see this message, the integration is working correctly."),
        html.button(
            {
                "style": {
                    "backgroundColor": "#4CAF50",
                    "color": "white",
                    "padding": "10px",
                    "borderRadius": "5px",
                    "border": "none",
                    "cursor": "pointer",
                },
            },
            "Click me!",
        ),
    )
