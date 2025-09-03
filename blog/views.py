import datetime

# import markdown
# from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.contrib import messages

# from django.db.models import Count
# from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

# from django.views.decorators.csrf import csrf_protect
from social_sharing.sharing import share_to_mastodon, share_to_bluesky

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
    """Home page view that displays a list of recent published posts."""
    # Fetch and paginate the data. Use prefetch/select_related for efficiency.
    post_list = (
        Post.objects.filter(status="published")
        .select_related("author")
        .prefetch_related("categories", "tags")
        .order_by("-published_date")
    )
    paginator = Paginator(post_list, 5)  # Show 5 posts per page
    page_number = request.GET.get("page")

    # Use get_page() which handles invalid page numbers gracefully
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)

    context = get_common_context()
    context.update(
        {
            "posts": page_obj,
            "page_obj": page_obj,
            "title": "Latest Posts",
        }
    )

    # Using request.htmx from django-htmx, decide which template to render
    if request.htmx:
        return render(request, "blog/partials/post_list.html", context)

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

    # Construct the title in the view
    if month is not None:
        month_name = datetime.date(2000, month, 1).strftime("%B")
        title = f"Archive:  Posts from {month_name} {year}"
    else:
        month_name = None
        title = f"Archive:  Posts from {year}"

    # Get common context data
    context = get_common_context()
    context.update(
        {
            "year": year,
            "month": month,
            "month_name": month_name,
            "posts": posts,
            "title": title,
        },
    )

    return render(request, "blog/archive_posts.html", context)


def search_posts(request):
    """View for searching posts by title, content, categories, and tags."""
    query = request.GET.get("q", "").strip()
    posts = Post.objects.filter(status="published")

    if query:
        # Search in post title, content, categories, and tags
        posts = (
            posts.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(categories__name__icontains=query)
                | Q(tags__name__icontains=query)
            )
            .distinct()
            .order_by("-published_date")
        )
    else:
        posts = posts.none()  # Return empty queryset if no query

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
            "query": query,
            "posts": posts,
            "query_params": {"q": query} if query else {},
        }
    )

    # return render(request, "blog/search_results.html", context)
    return render(request, "blog/search_posts.html", context)


# Share post view:  Mastodon and Bluesky
def share_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # post = get_object_or_404(Post, slug=slug, status="published")
    post_url = request.build_absolute_uri(post.get_absolute_url())

    if request.method == "POST":
        if "mastodon" in request.POST:
            result = share_to_mastodon(post.title, post_url)
            messages.success(request, result)
        elif "bluesky" in request.POST:
            result = share_to_bluesky(post.title, post_url)
            messages.success(request, result)
        else:
            # Handle the unlikely case that the form was submitted without a known button.
            messages.error(request, "Could not determine the sharing platform.")
            # Fallback to a full redirect even for HTMX requests on error.
            return redirect("blog:post_detail", slug=post.slug)

    # Check if the request is from HTMX
    if request.htmx:
        # If yes, return just the messages partial
        return render(request, "blog/partials/messages.html")

    # For non-HTMX requests, fall back to the old behavior
    return redirect("blog:post_detail", slug=post.slug)


# @staff_member_required
# @csrf_protect
# def markdown_preview(request):
#     """Render Markdown content to HTML for the admin preview. This view is only accessible to staff members."""
#     if request.method == "POST":
#         content = request.POST.get("content", "")
#         # Convert Markdown to HTML with syntax highlighting
#         html = markdown.markdown(
#             content,
#             extensions=[
#                 "markdown.extensions.fenced_code",
#                 "markdown.extensions.codehilite",
#                 "markdown.extensions.tables",
#                 "markdown.extensions.toc",
#             ],
#             extension_configs={
#                 "markdown.extensions.codehilite": {
#                     "css_class": "highlight",
#                     "linenums": False,
#                 },
#             },
#         )
#         return HttpResponse(html)
#     return HttpResponse("Method not allowed", status=405)
#
#
# def reactpy_demo(request):
#     """View for demonstrating ReactPy integration with Django."""
#     # Get common context data
#     # context = get_common_context()
#
#     # Render the HelloWorld component
#     # component = render_component(helloworld)
#
#     # Add the component to the context
#     # context["component"] = component
#
#     return render(request, "blog/reactpy_demo.html")

def about_me(request):
    return render(request, "blog/about_me.html")
