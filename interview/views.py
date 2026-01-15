from rest_framework import generics, permissions
from .models import InterviewSession
from .serializers import InterviewSessionSerializer

class InterviewListCreateView(generics.ListCreateAPIView):
    
    serializer_class = InterviewSessionSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        
        return InterviewSession.objects.filter(user=self.request.user).order_by('-start_time')

    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)