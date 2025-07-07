"""
ASGI config for byte_board_blog project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Ensure DJANGO_SETTINGS_MODULE is set properly based on your project name!
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "byte_board_blog.settings")

# Fetch ASGI application before importing dependencies that require ORM models.
django_asgi_app = get_asgi_application()


from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from reactpy_django import REACTPY_WEBSOCKET_ROUTE  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter([REACTPY_WEBSOCKET_ROUTE])),
    },
)
