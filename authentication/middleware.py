from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token):
    try:
        validated = AccessToken(token)
        return User.objects.get(id=validated["user_id"])
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()

class JWTChannelMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]

        scope["user"] = (
            await get_user_from_token(token)
            if token
            else AnonymousUser()
        )

        return await super().__call__(scope, receive, send)