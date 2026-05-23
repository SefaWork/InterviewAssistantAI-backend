from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = AccessToken(token_key)
        user_id = token["user_id"]
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()

class JWTChannelAuthMiddleware(BaseMiddleware):
    """This is a middleware class to implement JWT authentication for websockets. TODO: Change or depracate this logic in favor of one-time tickets."""
    async def __call__(self, scope, receive, send):
        # Try query string first: ws://.../?token=<jwt>
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_key = params.get("token", [None])[0]

        # Fall back to headers: Authorization: Bearer <jwt>
        if not token_key:
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()
            if auth_header.startswith("Bearer "):
                token_key = auth_header.split(" ", 1)[1]

        scope["user"] = (
            await get_user_from_token(token_key)
            if token_key
            else AnonymousUser()
        )

        return await super().__call__(scope, receive, send)