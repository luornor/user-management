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
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class RootAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Root API Endpoint",
        responses={200: openapi.Response('Successful operation', schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
    )
    def get(self, request, *args, **kwargs):
        api_urls = {
            'register': request.build_absolute_uri(reverse_lazy('register')),
            'login': request.build_absolute_uri(reverse_lazy('login')),
            'user-detail': request.build_absolute_uri(reverse_lazy('user-detail', args=[1])),
        }
        return Response(api_urls, status=status.HTTP_200_OK)


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User Registration",
        responses={201: UserSerializer()},

    )
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

    @swagger_auto_schema(
        operation_summary="User Detail",
        responses={200: UserSerializer(), 404: "User not found"},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update User",
        responses={200: UserSerializer(), 400: "Invalid input"},
    )
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Delete User",
        responses={204: "User deleted successfully", 404: "User not found"},
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "User Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User Login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'password'],
        ),
        responses={200: openapi.Response('Login successful. Token generated successfully.',UserSerializer())},
    )
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
