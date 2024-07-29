from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': False},  # Allow email to be optional
        }


    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            role=validated_data['role'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.role = validated_data.get('role', instance.role)

        password = validated_data.get('password')
        if password:
            instance.set_password(password)

        instance.save()
        return instance
