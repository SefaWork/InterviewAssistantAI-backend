from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

@database_sync_to_async
def get_user_from_ticket(ticket):
    try:
        user_id = cache.get(f"ws_ticket:{ticket}")
        cache.delete(f"ws_ticket:{ticket}")
        if not user_id:
            return AnonymousUser()

        return User.objects.get(id=user_id)
    except:
        return AnonymousUser()

class TicketChannelMiddleware(BaseMiddleware):
    """This is a middleware class to implement JWT authentication for websockets. TODO: Change or depracate this logic in favor of one-time tickets."""
    async def __call__(self, scope, receive, send):
        # Try query string first: ws://.../?token=<jwt>
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        ticket_key = params.get("ticket", [None])[0]

        scope["user"] = (
            await get_user_from_ticket(ticket_key)
            if ticket_key
            else AnonymousUser()
        )

        return await super().__call__(scope, receive, send)