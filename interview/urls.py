from django.urls import path
from .views import InterviewCreateView, InterviewContinueView

urlpatterns = [
    path('create/', InterviewCreateView.as_view(), name="create_session"),
    path('continue/<uuid:session_id>/', InterviewContinueView.as_view(), name="continue_session")
]