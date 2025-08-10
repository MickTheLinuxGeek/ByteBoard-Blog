# blog/admin.py

from typing import ClassVar
from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import Category, Post, Tag

from django.db import models
from .widgets import MarkdownTextarea


# 1. Define your Custom Admin Site
# ----------------------------------
class BlogAdminSite(admin.AdminSite):
    """A custom AdminSite for the blog application."""

    site_header = "Byte Board Blog Administration"
    site_title = "My Blog Admin Portal"
    index_title = "Welcome to the Byte Board Blog Admin System"


# 2. Create an instance of your custom site
# -------------------------------------------
blog_admin_site = BlogAdminSite(name="blog_admin")


# 3. Define your ModelAdmin classes as before, but WITHOUT the decorator
# ----------------------------------------------------------------------
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields: ClassVar = {"slug": ("name",)}
    search_fields = ("name",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields: ClassVar = {"slug": ("name",)}
    search_fields = ("name",)


class PostAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            # None,
            "Blog Post Editor",
            {
                "fields": (
                    "title",
                    "slug",
                    "author",
                    "content",
                    "status",
                    "categories",
                    "tags",
                )
            },
        ),
        (
            "SEO Section",
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                    "image",
                    "og_title",
                    "og_description",
                ),
                "description": "Per post meta information.",
            },
        ),
    )

    list_display = (
        "title",
        "slug",
        "author",
        "status",
        "created_at",
        "published_date",
    )
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
    actions: ClassVar = ["publish_posts", "unpublish_posts"]

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Hook to specify a custom widget for a particular field.
        """
        # Check if the field is a TextField, which is what we want for Markdown content.
        if isinstance(db_field, models.TextField):
            kwargs["widget"] = MarkdownTextarea()

        # For all other fields, use the default widget.
        return super().formfield_for_dbfield(db_field, **kwargs)

    class Media:
        css = {
            # Highlight.js CSS (choose a theme you like from the cdnjs website)
            "all": (
                "easymde/easymde.min.css",
                "css/custom_admin.css",  # Your custom styles now load here
                "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css",
            )
        }
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js",
        )

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


# 4. Register your models and their admin classes with your CUSTOM site instance
# ------------------------------------------------------------------------------
blog_admin_site.register(Category, CategoryAdmin)
blog_admin_site.register(Tag, TagAdmin)
blog_admin_site.register(Post, PostAdmin)

# You can also register other models like User and Group if you want them
# in your custom admin.
blog_admin_site.register(User)
blog_admin_site.register(Group)
