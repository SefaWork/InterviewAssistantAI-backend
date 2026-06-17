from django.urls import path
from .views import InterviewCreateView, EmotionWeightsView, InterviewForceCreateView

urlpatterns = [
    path('create/', InterviewCreateView.as_view(), name="create_session"),
    path('forcecreate/', InterviewForceCreateView.as_view(), name="force_create_session"),
    path('weights/', EmotionWeightsView.as_view(), name="get_emotion_weights")
]