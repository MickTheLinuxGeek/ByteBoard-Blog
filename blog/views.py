import datetime

import markdown
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect

from .models import Category, Post, Tag


def get_common_context():
    """Helper function to get common context data for all views."""
    categories = Category.objects.all()
    tags = Tag.objects.all()

    # Get archive dates (years and months with posts)
    published_dates = Post.objects.filter(status="published").dates(
        "published_date",
        "month",
        order="DESC",
    )

    archive_dates = []
    years_dict = {}

    for date in published_dates:
        year = date.year
        month = date.month

        if year not in years_dict:
            years_dict[year] = {"year": year, "months": []}

        if month not in years_dict[year]["months"]:
            years_dict[year]["months"].append(month)

    for year, data in sorted(years_dict.items(), reverse=True):
        archive_dates.append(
            {"year": year, "months": sorted(data["months"], reverse=True)},
        )

    return {"categories": categories, "tags": tags, "archive_dates": archive_dates}


def home(request):
    """Home page view that displays a list of recent published posts."""
    posts = (
        Post.objects.select_related(
            "author",
        )  # select_related and prefetch_related added!
        .prefetch_related("categories", "tags")
        .filter(status="published")
        .order_by("-published_date")
    )
    # posts = Post.objects.filter(status="published").order_by("-published_date")

    # Pagination
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page = request.GET.get("page")

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)

    # Get common context data
    context = get_common_context()
    context["posts"] = posts

    return render(request, "blog/home.html", context)


def post_detail(request, slug):
    """View for displaying a single post."""
    post = get_object_or_404(Post, slug=slug, status="published")

    # Get common context data
    context = get_common_context()
    context["post"] = post

    return render(request, "blog/post_detail.html", context)


def category_posts(request, slug):
    """View for displaying posts in a specific category."""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(categories=category, status="published").order_by(
        "-published_date",
    )

    # Pagination
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page = request.GET.get("page")

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Get common context data
    context = get_common_context()
    context["category"] = category
    context["posts"] = posts

    return render(request, "blog/category_posts.html", context)


def tag_posts(request, slug):
    """View for displaying posts with a specific tag."""
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, status="published").order_by(
        "-published_date",
    )

    # Pagination
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page = request.GET.get("page")

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Get common context data
    context = get_common_context()
    context["tag"] = tag
    context["posts"] = posts

    return render(request, "blog/tag_posts.html", context)


def archive_posts(request, year, month=None):
    """View for displaying posts from a specific year and month."""
    posts = Post.objects.filter(status="published")

    if year:
        posts = posts.filter(published_date__year=year)

    if month:
        posts = posts.filter(published_date__month=month)

    posts = posts.order_by("-published_date")

    # Pagination
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page = request.GET.get("page")

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Get common context data
    context = get_common_context()
    context.update(
        {
            "year": year,
            "month": month,
            "month_name": datetime.date(2000, month, 1).strftime("%B")
            if month
            else None,
            "posts": posts,
        },
    )

    return render(request, "blog/archive_posts.html", context)


@staff_member_required
@csrf_protect
def markdown_preview(request):
    """Render Markdown content to HTML for the admin preview. This view is only accessible to staff members."""
    if request.method == "POST":
        content = request.POST.get("content", "")
        # Convert Markdown to HTML with syntax highlighting
        html = markdown.markdown(
            content,
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
        return HttpResponse(html)
    return HttpResponse("Method not allowed", status=405)


def reactpy_demo(request):
    """View for demonstrating ReactPy integration with Django."""
    # Get common context data
    # context = get_common_context()

    # Render the HelloWorld component
    # component = render_component(helloworld)

    # Add the component to the context
    # context["component"] = component

    return render(request, "blog/reactpy_demo.html")
