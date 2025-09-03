import markdown

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def convert_markdown(value):
    return markdown.markdown(value, extensions=["markdown.extensions.fenced_code"])


@register.filter(name="month_name")
def month_name(month_number):
    """Converts a month number (1-12) to its full name."""
    months = [
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
    try:
        # Adjust for 0-based index
        return months[int(month_number) - 1]
    except (ValueError, IndexError):
        return ""  # Return empty string for invalid input
