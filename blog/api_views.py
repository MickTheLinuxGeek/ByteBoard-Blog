from typing import ClassVar

from django.utils import timezone
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Category, Post, Tag
from .serializers import (
    CategorySerializer,
    PostDetailSerializer,
    PostListSerializer,
    TagSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API views."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing categories."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes: ClassVar = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends: ClassVar = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar = ["name"]
    ordering_fields: ClassVar = ["name"]
    lookup_field = "slug"


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends: ClassVar = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar = ["name"]
    ordering_fields: ClassVar = ["name"]
    lookup_field = "slug"


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing posts."""

    queryset = Post.objects.filter(
        status="published",
        published_date__lte=timezone.now(),
    ).order_by("-published_date")
    permission_classes: ClassVar = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends: ClassVar = [filters.SearchFilter, filters.OrderingFilter]
    search_fields: ClassVar = ["title", "content"]
    ordering_fields: ClassVar = ["published_date", "created_at", "title"]
    lookup_field = "slug"

    def get_serializer_class(self):
        """Return different serializers for list and detail views."""
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer
