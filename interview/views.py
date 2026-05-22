from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import InterviewSession
from .serializers import InterviewSessionCreateSerializer

class InterviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session = InterviewSession.objects.create(user=request.user)
        serializer = InterviewSessionCreateSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)