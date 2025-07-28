"""
URL configuration for byte_board_blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from blog.admin import blog_admin_site

from blog.views import markdown_preview

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin/blog/post/preview/", markdown_preview, name="markdown_preview"),
    path("", include("blog.urls")),  # Include the blog app URLs
    path("api/", include("blog.api_urls")),  # Include the blog app API URLs
    path("reactpy/", include("reactpy_django.http.urls")),
    path("my-blog-admin/", blog_admin_site.urls, name="my-blog-admin"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
