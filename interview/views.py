from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from .emotion_weights import EMOTION_SCORE_WEIGHTS
from .models import OngoingInterviewSession, InterviewSession
from .serializers import InterviewSessionSerializer


from .ai_processor import InterviewAI


ai_engine = InterviewAI()

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


class InterviewSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = InterviewSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InterviewSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnalyzeFrameView(APIView):
    def post(self, request, format=None):
        if 'image' not in request.data:
            return Response(
                {"error": "Resim bulunamadı. Lütfen 'image' anahtarı ile Base64 metni gönderin."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        image_data = request.data['image']
        
        
        result = ai_engine.process_frame(image_data)

        return Response(result)