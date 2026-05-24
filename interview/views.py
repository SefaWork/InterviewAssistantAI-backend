from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import InterviewSession
from .serializers import InterviewSessionCreateSerializer

import secrets
from django.core.cache import cache

class InterviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Create session.
        session = InterviewSession.objects.create(user=request.user)
        serializer = InterviewSessionCreateSerializer(session)

        # Create access ticket.
        ticket = secrets.token_urlsafe(32)
        cache.set(f"ws_ticket:{ticket}", request.user.id, timeout=30)
        return Response({**serializer.data, "ticket": ticket}, status=status.HTTP_201_CREATED)