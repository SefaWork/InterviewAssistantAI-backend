from django.urls import path
from .views import CookieTokenRefreshView, CookieTokenObtainPairView

urlpatterns = [
    #path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
]