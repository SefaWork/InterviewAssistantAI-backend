from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/stream/(?P<session_id>[0-9a-f-]+)/$", consumers.ImageStreamConsumer.as_asgi()),
]