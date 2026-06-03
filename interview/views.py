from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import OngoingInterviewSession

class InterviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Reject if user has an ongoing session.
        if OngoingInterviewSession.objects.filter(user=request.user).exists():
            return Response({"error": "You already have an ongoing session."}, status=status.HTTP_409_CONFLICT)

        # Create session.
        OngoingInterviewSession.objects.create(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

