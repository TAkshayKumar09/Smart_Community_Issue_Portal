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

        # CHECK IF USER EXISTS
        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"error": "User already exists. Please login."},
                status=400
            )

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
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
                }

                # create token
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
                # response
                response = JsonResponse({"message": "Login successful","user": {"name": check.name,"email": check.email,"is_admin": check.is_admin}})

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
            return JsonResponse({"error": "Invalid credentials"}, status=400)
    return JsonResponse({"error": "Invalid Request Method"}, status=405)

@csrf_exempt
def get_user(req):
    token = req.COOKIES.get("token")

    if not token:
        return JsonResponse({"error": "Not logged in"}, status=401)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload["user_id"])

        return JsonResponse({
            "name": user.name,
            "email": user.email,
            "phone": user.phone
        })
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Token expired"}, status=401)

    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid token"}, status=401)


@csrf_exempt
def update_user(req):
    if req.method == "POST":
        token = req.COOKIES.get("token")

        if not token:
            return JsonResponse({"error": "Not logged in"}, status=401)

        try:
            # Decode token
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            # Get data
            name = req.POST.get("name")
            email = req.POST.get("email")
            phone = req.POST.get("phone")
            old_password = req.POST.get("old_password")
            new_password = req.POST.get("new_password")

            # Update basic details
            if name:
                user.name = name
            if email:
                user.email = email
            if phone:
                user.phone = phone

            # Password change (optional)
            if old_password and new_password:
                import bcrypt

                is_match = bcrypt.checkpw(
                    old_password.encode("utf-8"),
                    user.password.encode("utf-8")
                )

                if not is_match:
                    return JsonResponse({"error": "Old password incorrect"}, status=400)

                # hash new password
                hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
                user.password = hashed.decode("utf-8")

            # Save changes
            user.save()

            return JsonResponse({"message": "Profile updated successfully"})

        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired"}, status=401)

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)       

