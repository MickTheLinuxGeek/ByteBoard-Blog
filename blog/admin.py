from typing import ClassVar

from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import Category, Post, Tag


class MarkdownTextarea(Textarea):
    """Custom widget for Markdown editing."""

    def __init__(self, attrs=None):
        default_attrs = {"class": "markdown-editor"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields: ClassVar = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields: ClassVar = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "author", "status", "created_at", "published_date")
    list_filter = (
        "status",
        "created_at",
        "published_date",
        "author",
        "categories",
        "tags",
    )
    search_fields = ("title", "content")
    prepopulated_fields: ClassVar = {"slug": ("title",)}
    raw_id_fields = ("author",)
    date_hierarchy = "published_date"
    ordering = ("status", "-published_date")
    filter_horizontal = ("categories", "tags")

    # Add Markdown editor for content field
    formfield_overrides: ClassVar = {
        models.TextField: {"widget": MarkdownTextarea},
    }

    actions: ClassVar = ["publish_posts", "unpublish_posts"]

    def publish_posts(self, request, queryset):
        """Admin action to publish multiple posts at once."""
        updated = queryset.update(status="published")
        self.message_user(request, f"{updated} posts have been published.")

    publish_posts.short_description = "Publish selected posts"

    def unpublish_posts(self, request, queryset):
        """Admin action to unpublish multiple posts at once."""
        updated = queryset.update(status="draft", published_date=None)
        self.message_user(request, f"{updated} posts have been unpublished.")

    unpublish_posts.short_description = "Unpublish selected posts"
