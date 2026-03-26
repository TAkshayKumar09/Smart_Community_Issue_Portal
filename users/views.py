from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
import bcrypt
import jwt
import datetime
from django.conf import settings
SECRET_KEY=settings.SECRET_KEY

# Create your views here.


@csrf_exempt
def register(req):
    if req.method == "POST":
        name = req.POST.get('name')
        phone = req.POST.get('phone')
        email = req.POST.get('email')
        password = req.POST.get('password')

        # VALIDATIONS
        if not name or not phone or not email or not password:
            return JsonResponse({"error": "All fields are required"}, status=400)

        if len(password) < 6:
            return JsonResponse({"error": "Password too short"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        hashed = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt(rounds=12)).decode('utf-8')
    Users = User.objects.create(name=name, phone=phone, email=email, password=hashed)
    return HttpResponse('User created successfully')

@csrf_exempt
def login(req):
    if req.method == "POST":
        email = req.POST.get('email')
        password = req.POST.get('password')

         # VALIDATIONS
        if not email or not password:
            return JsonResponse({"error": "Email and password required"}, status=400)

        try:
            check = User.objects.get(email=email)
            stored_hash = check.password

            is_same = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            if is_same:
                # creating jwt
                payload ={
                    "user_id": check.id,
                    "is_admin": check.is_admin,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
                }

                # create token
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                # response
                response = JsonResponse({"message": "Login successful","is_admin": check.is_admin})

                # set cookie
                response.set_cookie(
                    key="token",
                    value=token,
                    httponly=True,
                    secure=True,
                    samesite="None"
                )

                return response
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=400)
        
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
    return JsonResponse({"error": "Invalid Request Method"}, status=405)

@csrf_exempt
def get_profile(req, email):
    if req.method == "GET":

        try:
            user = User.objects.get(email=email)

            return JsonResponse({
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
            })
        except User.DoesNotExist:
            return JsonResponse("User not found", status=404)
    return JsonResponse("Invalid request", status=400)
            


            

