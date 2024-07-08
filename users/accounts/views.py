from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
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
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "User Deleted successfully."},status=status.HTTP_204_NO_CONTENT)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({"message": "Missing email or password"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(email=email, password=password)
        if user:
            token = super().post(request, *args, **kwargs)
            return Response({
                "message": "Login successful. Token generated successfully.",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "token": token.data['access']
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
