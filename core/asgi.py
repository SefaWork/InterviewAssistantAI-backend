import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from interview import routing
from authentication.middleware import JWTChannelMiddleware
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator( # Limit allowed hosts.
        JWTChannelMiddleware( # Implement JWT authentication for websocket.
            URLRouter(routing.websocket_urlpatterns)
        )
    )
})