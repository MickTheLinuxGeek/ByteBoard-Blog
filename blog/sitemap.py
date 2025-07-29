from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Post, Category, Tag


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.filter(status="published").order_by("-published_date")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("blog:post_detail", args=[obj.slug])


class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse("blog:category_posts", args=[obj.slug])


class TagSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return reverse("blog:tag_posts", args=[obj.slug])


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ["blog:home"]

    def location(self, item):
        return reverse(item)