from django.urls import path
from .views import InterviewCreateView

urlpatterns = [
    path('create/', InterviewCreateView.as_view(), name="create_session")
]