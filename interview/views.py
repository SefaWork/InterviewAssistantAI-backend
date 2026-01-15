from rest_framework import generics, permissions
from .models import InterviewSession
from .serializers import InterviewSessionSerializer
from .ai_processor import InterviewAI
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

class InterviewListCreateView(generics.ListCreateAPIView):
    
    serializer_class = InterviewSessionSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        
        return InterviewSession.objects.filter(user=self.request.user).order_by('-start_time')

    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)

class AnalyzeFrameView(APIView):

    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        if 'image' not in request.data:
            return Response({"error": "Resim bulunamadı"}, status=400)

        image_file = request.data['image']
        image_bytes = image_file.read()

        ai_engine = InterviewAI()
        result = ai_engine.process_frame(image_bytes)

        return Response(result)