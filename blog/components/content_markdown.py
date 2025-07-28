from reactpy import component, html
import markdown
# from markdown_it import MarkdownIt

# md = MarkdownIt()


@component
def Markdown(source: str):
    # html_string = md.render(source)
    html_string = markdown.markdown(
        source,
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.codehilite",
        ],
    )

    # Add this print statement for debugging
    print("--- Generated HTML ---")
    print(html_string)
    print("----------------------")

    return html.div(
        {
            "dangerouslySetInnerHTML": {"__html": html_string},
            "className": "markdown-view",
        },
    )
