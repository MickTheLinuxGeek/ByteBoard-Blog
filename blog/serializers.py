from typing import ClassVar

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Category, Post, Tag


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = User
        fields: ClassVar = ["id", "username", "first_name", "last_name"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""

    class Meta:
        model = Category
        fields: ClassVar = ["id", "name", "slug"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag model."""

    class Meta:
        model = Tag
        fields: ClassVar = ["id", "name", "slug"]


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for listing Post instances."""

    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields: ClassVar = [
            "id",
            "title",
            "slug",
            "author",
            "status",
            "categories",
            "tags",
            "created_at",
            "updated_at",
            "published_date",
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed Post instance."""

    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields: ClassVar = [
            "id",
            "title",
            "slug",
            "author",
            "content",
            "status",
            "categories",
            "tags",
            "created_at",
            "updated_at",
            "published_date",
        ]
