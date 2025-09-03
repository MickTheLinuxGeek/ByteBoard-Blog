import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown_filter")
@stringfilter
def markdown_filter(value):
    """
    Converts a markdown string to HTML, preserving code highlighting.
    """
    html = markdown.markdown(
        value,
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.codehilite",
            "markdown.extensions.tables",
            "markdown.extensions.toc",
        ],
        extension_configs={
            "markdown.extensions.codehilite": {
                "css_class": "highlight",
                "linenums": False,
            },
        },
    )
    return mark_safe(html)
