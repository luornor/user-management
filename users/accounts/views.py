from django.conf import settings
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.decorators import method_decorator
import json
import jwt
import logging
from .models import CustomUser
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    """
    post:
    Register a new user.
    
    Parameters:
    - email: string
    - username: string
    - role: string
    - password1: string
    - password2: string

    Responses:
    - 200: User created successfully
    - 400: Missing parameters or passwords do not match
    - 500: Server error
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            username = data.get("username")
            role = data.get("role")
            password1 = data.get("password1")
            password2 = data.get("password2")

            if not all([email, username, role, password1, password2]):
                return JsonResponse({"message": "Missing parameters in request", "status": 400}, status=400)

            if password1 != password2:
                return JsonResponse({"message": "Passwords do not match", "status": 400}, status=400)
            
            user = CustomUser.objects.create_user(username=username, email=email, role=role, password=password1)
            user.save()

            response_data = {
                "message": "User created successfully. You can login now",
                "status": 200,
                "data": {
                    "user_id":user.id,
                    "username": user.username,
                    "email": user.email, "role": user.role},
            }

            return JsonResponse(response_data, content_type="application/json")

        except json.JSONDecodeError:
            logger.exception("JSONDecodeError: You might have forgotten to provide your data/field(s) in JSON format.")
            return JsonResponse({"message": "Invalid JSON format", "status": 400}, status=400)
        except Exception as e:
            logger.exception("An error occurred")
            return JsonResponse({"message": "An error occurred: " + str(e), "status": 500}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):
    """
    get:
    Retrieve a user by ID.
    
    put:
    Update a user's details by ID.
    
    delete:
    Delete a user by ID.
    """
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(pk=id)
            response_data = {
                        "user_id":user.id,
                        "username": user.username,
                        "email": user.email, "role": user.role}
            return JsonResponse({"status": 200, "data": response_data}, status=200)
        except CustomUser.DoesNotExist:
            return JsonResponse({"status": 404, "message": "User not found"}, status=404)

    def put(self, request, id):
        try:
            data = json.loads(request.body)
            user = CustomUser.objects.get(pk=id)

            user.username = data.get("username", user.username)
            user.email = data.get("email", user.email)
            if 'password' in data:
                user.set_password(data['password'])

            user.save()

            response_data = {"user_id":user.id,
                            "username": user.username, 
                            "email": user.email,
                            "role": user.role}
            return JsonResponse({"status": 200, "message": "User updated successfully", "data": response_data}, status=200)
        except CustomUser.DoesNotExist:
            return JsonResponse({"status": 404, "message": "User not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"status": 400, "message": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"status": 500, "message": f"An error occurred: {str(e)}"}, status=500)

    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(pk=id)
            user.delete()
            return JsonResponse({"status": 200, "message": "User deleted successfully"}, status=200)
        except CustomUser.DoesNotExist:
            return JsonResponse({"status": 404, "message": "User not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": 500, "message": f"An error occurred: {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    """
    post:
    Log in a user.

    Parameters:
    - email: string
    - password: string

    Responses:
    - 200: Login successful
    - 400: Missing parameters or invalid credentials
    - 500: Server error
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            if not all([email, password]):
                return JsonResponse({"message": "Missing email or password", "status": 400}, status=400)

            user = authenticate(email=email, password=password)
            if user is not None:
                payload = {'user_id': user.id, 'email': user.email}
                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                message = "Login successful. Token generated successfully."
                return JsonResponse({
                                    "message": message,
                                    "user_id": user.id,
                                    'username': user.username,
                                    'email': user.email,
                                    'role': user.role,
                                    "token": token}, status=200)
            else:
                return JsonResponse({"status": 401, "message": "Invalid credentials"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON format", "status": 400}, status=400)
        except Exception as e:
            return JsonResponse({"message": "An error occurred: " + str(e), "status": 500}, status=500)
