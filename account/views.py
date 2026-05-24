from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from interview.models import InterviewSession
from .serializers import SessionListSerializer, SessionDisplaySerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status

User = get_user_model()

# Returns list of past interviews as response.
class SessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = 10
        offset = (page - 1) * page_size

        sessions = InterviewSession.objects.filter(user=request.user).order_by("-created_at")[offset:offset + page_size]
        serializer = SessionListSerializer(sessions, many=True)
        return Response(serializer.data)

# Gives more detailed information about a specific session.
class SessionDisplayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        session = get_object_or_404(InterviewSession, pk=pk, user=request.user)
        serializer = SessionDisplaySerializer(session)
        return Response(serializer.data)

class DeleteSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        session_id = request.data.get('session_id')

        if not session_id:
            return Response({"error": "Session ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        session = get_object_or_404(InterviewSession, id=session_id, user=user)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        password = request.data.get("password")
        new_email = request.data.get("new_email")

        if not new_email or not password:
            return Response({"error": "Both fields are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(password):
            return Response({"error": "Password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_email(new_email)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            return Response({"error": "E-mail is already in use."}, status=status.HTTP_409_CONFLICT)

        user.email = new_email
        user.save()
        return Response({"message": "E-mail changed successfully."}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        
        if not current_password or not new_password:
            return Response({"error": "Both fields are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(current_password):
            return Response({"error": "Password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        password = request.data.get("password")

        if not password:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({"error": "Password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)