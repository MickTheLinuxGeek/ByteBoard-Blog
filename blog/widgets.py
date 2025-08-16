# blog/widgets.py

from django import forms


class MarkdownTextarea(forms.Textarea):
    """
    A custom widget to render a textarea as a an EasyMDE Markdown editor.
    """

    def __init__(self, attrs=None):
        default_attrs = {"class": "markdown-editor"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        """
        Media class to include the necessary CSS and JS files for the widget.
        Django will automatically include these in the <head> of the admin page.
        """

        # css = {
        #     "all": (
        #         "easymde/easymde.min.css",
        #         "css/custom_admin.css",
        #     )
        # }
        js = (
            "easymde/easymde.min.js",
            "js/markdown-editor.js",  # Our custom initializer
        )
