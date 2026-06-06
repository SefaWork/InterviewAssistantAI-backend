from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .emotion_weights import EMOTION_SCORE_WEIGHTS
from .models import OngoingInterviewSession

class InterviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        if OngoingInterviewSession.objects.filter(user=request.user).exists():
            return Response({"error": "You already have an ongoing session."}, status=status.HTTP_409_CONFLICT)

        
        OngoingInterviewSession.objects.create(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmotionWeightsView(APIView):
    def get(self, request):
        return Response(EMOTION_SCORE_WEIGHTS, status=status.HTTP_200_OK)