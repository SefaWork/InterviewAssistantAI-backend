from django.urls import path
from .views import SessionListView, SessionDisplayView

urlpatterns = [
    path('interviews/', SessionListView.as_view(), name="list_interviews"),
    path('interviews/<uuid:pk>/', SessionDisplayView.as_view(), name="display_interview")
]