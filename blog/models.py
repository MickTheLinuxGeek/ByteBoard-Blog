from typing import ClassVar

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# Create your models here.
class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering: ClassVar = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering: ClassVar = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(BaseModel):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    categories = models.ManyToManyField(Category, related_name="posts")
    tags = models.ManyToManyField(Tag, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(null=True, blank=True)
    meta_title = models.CharField(
        max_length=60, blank=True, help_text="Optimal length: 50-60 characters"
    )
    meta_description = models.CharField(
        max_length=160, blank=True, help_text="Optimal length: 150-160 characters"
    )
    image = models.ImageField(
        upload_to="post_images/",
        blank=True,
        null=True,
        help_text="Image for the blog post and Open Graph preview.",
    )

    # You can reuse meta_title and meta_description, or add specific OG fields:
    og_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Open Graph title. If blank, uses meta title or post title.",
    )
    og_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Open Graph description. If blank, uses meta description.",
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering: ClassVar = ["-published_date", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.status == "published" and not self.published_date:
            self.published_date = timezone.now()

        # --- NEW: Automatically populate OG fields if they are empty ---
        if not self.og_title:
            # Use the meta_title if available, otherwise use the main title
            self.og_title = self.meta_title if self.meta_title else self.title

        if not self.og_description:
            # Use the meta_description if available, otherwise truncate the content
            if self.meta_description:
                self.og_description = self.meta_description
            else:
                # A simple way to get a plain text summary
                plain_content = self.content.replace("\n", " ").replace("\r", "")
                self.og_description = (
                    (plain_content[:157] + "...")
                    if len(plain_content) > 160
                    else plain_content
                )
        # --- End of new code ---

        super().save(*args, **kwargs)

    def publish(self):
        """Method to publish a draft post."""
        self.status = "published"
        self.published_date = timezone.now()
        self.save()

    def unpublish(self):
        """Method to unpublish a post and return it to draft status."""
        self.status = "draft"
        self.published_date = None
        self.save()
