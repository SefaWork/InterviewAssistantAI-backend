from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .models import InterviewSession
from .serializers import InterviewSessionSerializer
from .ai_processor import InterviewAI


ai_engine = InterviewAI()


class InterviewSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = InterviewSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        
        return InterviewSession.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class AnalyzeFrameView(APIView):
    parser_classes = [MultiPartParser]
    

    def post(self, request, format=None):
        
        if 'image' not in request.data:
            return Response({"error": "Resim bulunamadı. Lütfen 'image' anahtarı ile gönderin."}, status=400)

        image_file = request.data['image']
        image_bytes = image_file.read()

        
        result = ai_engine.process_frame(image_bytes)

        return Response(result)