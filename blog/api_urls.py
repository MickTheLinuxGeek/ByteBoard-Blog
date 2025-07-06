from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import CategoryViewSet, PostViewSet, TagViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"tags", TagViewSet)
router.register(r"posts", PostViewSet)

# The API URLs are determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
