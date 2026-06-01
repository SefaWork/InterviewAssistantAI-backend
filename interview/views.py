from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import OngoingInterviewSession
from .serializers import InterviewSessionCreateSerializer

class InterviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Reject if user has an ongoing session.
        ongoing = request.user.interview_sessions.first()
        if ongoing:
            return Response(
                {
                    "error": "You already have an ongoing session.",
                    "session_id": str(ongoing.id) # Send the ID to the server so they can request to continue that session.
                },
                status=status.HTTP_409_CONFLICT
            )

        # Create session.
        session = OngoingInterviewSession.objects.create(user=request.user)
        serializer = InterviewSessionCreateSerializer(session)

        return Response(serializer.data, status=status.HTTP_201_CREATED)