from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.urls import reverse_lazy

class RootAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        api_urls = {
             'register': request.build_absolute_uri(reverse_lazy('register')),
            'login': request.build_absolute_uri(reverse_lazy('login')),
            'user-detail': request.build_absolute_uri(reverse_lazy('user-detail', args=[1])),  # Example with id=1
         }
        return Response(api_urls, status=status.HTTP_200_OK)
    

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": "User created successfully. You can login now", "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({"message": "Missing email or password"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)
        if user:
            payload = {'user_id': user.id, 'email': user.email}
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            return Response({
                "message": "Login successful. Token generated successfully.",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "token": token
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
