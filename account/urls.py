from django.urls import path
from .views import SessionListView, SessionDisplayView, ChangeEmailView, ChangePasswordView, DeleteSessionView, DeleteAccountView

urlpatterns = [
    path('interviews/', SessionListView.as_view(), name="list_interviews"),
    path('interviews/<uuid:pk>/', SessionDisplayView.as_view(), name="display_interview"),
    path('delete-interview/', DeleteSessionView.as_view(), name="delete_interview"),
    path('change-password/', ChangePasswordView.as_view(), name="change_password"),
    path('change-email/', ChangeEmailView.as_view(), name="change_email"),
    path('delete-account/', DeleteAccountView.as_view(), name="delete_account")
]