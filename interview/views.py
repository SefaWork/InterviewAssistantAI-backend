from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import InterviewSession
from .serializers import InterviewSessionCreateSerializer

import secrets
from django.core.cache import cache
from django.shortcuts import get_object_or_404

class InterviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Reject if user has an ongoing session.
        ongoing = InterviewSession.objects.filter(user=request.user, completed=False).first()
        if ongoing:
            return Response(
                {
                    "error": "You already have an ongoing session.",
                    "session_id": str(ongoing.id) # Send the ID to the server so they can request to continue that session.
                },
                status=status.HTTP_409_CONFLICT
            )

        # Create session.
        session = InterviewSession.objects.create(user=request.user)
        serializer = InterviewSessionCreateSerializer(session)

        # Create access ticket.
        ticket = secrets.token_urlsafe(32)
        cache.set(f"ws_ticket:{ticket}", request.user.id, timeout=30)
        return Response({**serializer.data, "ticket": ticket}, status=status.HTTP_201_CREATED)

class InterviewContinueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        if not InterviewSession.objects.filter(user=request.user, id=session_id, completed=False).exists():
            return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Create access ticket. 
        ticket = secrets.token_urlsafe(32)
        cache.set(f"ws_ticket:{ticket}", request.user.id, timeout=30)

        # Client already knows session id, no need to send it again.
        return Response({"ticket": ticket}, status=status.HTTP_200_OK)