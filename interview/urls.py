from django.urls import path
from .views import InterviewSessionListCreateView, AnalyzeFrameView

urlpatterns = [
    path('sessions/', InterviewSessionListCreateView.as_view(), name='session-list-create'),
    path('analyze/', AnalyzeFrameView.as_view(), name='analyze'), 
]