from django.urls import path
from .views import RegisterView, UserDetailView, LoginView,RootAPIView


urlpatterns = [
    path('', RootAPIView.as_view(), name='root-api'),
    path('users/register/', RegisterView.as_view(), name='register'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
]
