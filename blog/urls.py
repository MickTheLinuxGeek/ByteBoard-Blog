from django.contrib.syndication.views import Feed
from django.urls import path
from django.utils.feedgenerator import Atom1Feed

from . import views
from .models import Post

app_name = "blog"

RSS_ITEM_DESCRIPTION_LENGTH = 200


# RSS Feed class
class LatestPostsFeed(Feed):
    title = "Byte Board Blog"
    link = "/"
    description = "Latest posts from Byte Board Blog"

    def items(self):
        return Post.objects.filter(status="published").order_by("-published_date")[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return (
            item.content[:200] + "..."
            if len(item.content) > RSS_ITEM_DESCRIPTION_LENGTH
            else item.content
        )

    def item_link(self, item):
        return f"/post/{item.slug}/"


# Atom Feed class
class AtomLatestPostsFeed(LatestPostsFeed):
    feed_type = Atom1Feed
    subtitle = LatestPostsFeed.description


urlpatterns = [
    # Home page
    path("", views.home, name="home"),
    # Post detail
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    # Category posts
    path("category/<slug:slug>/", views.category_posts, name="category_posts"),
    # Tag posts
    path("tag/<slug:slug>/", views.tag_posts, name="tag_posts"),
    # Archive posts
    path("archive/<int:year>/", views.archive_posts, name="year_archive"),
    path("archive/<int:year>/<int:month>/", views.archive_posts, name="month_archive"),
    # RSS and Atom feeds
    path("feed/rss/", LatestPostsFeed(), name="rss_feed"),
    path("feed/atom/", AtomLatestPostsFeed(), name="atom_feed"),
]
