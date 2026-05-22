from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from interview.models import InterviewSession
from .serializers import SessionListSerializer, SessionDisplaySerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Returns list of past interviews as response.
class SessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = 10
        offset = (page - 1) * page_size

        sessions = InterviewSession.objects.filter(user=request.user)[offset:offset + page_size]
        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data)

# Gives more detailed information about a specific session.
class SessionDisplayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
        serializer = SessionDisplaySerializer(session)
        return Response(serializer.data)