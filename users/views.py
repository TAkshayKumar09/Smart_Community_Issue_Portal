from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User
import bcrypt

# Create your views here.


@csrf_exempt
def register(req):
    if req.method == "POST":
        name = req.POST.get('name')
        phone = req.POST.get('phone')
        email = req.POST.get('email')
        password = req.POST.get('password')

        hashed = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt(rounds=12)).decode('utf-8')
    Users = User.objects.create(name=name, phone=phone, email=email, password=hashed)
    return HttpResponse('User created successfully')

@csrf_exempt
def login(req):
    if req.method == "POST":
        email = req.POST.get('email')
        password = req.POST.get('password')

        try:
            check = User.objects.get(email=email)
            stored_hash = check.password

            is_same = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            if is_same:
                return HttpResponse("Login Successfully", status = 200)
            else:
                return HttpResponse("Invalid credentials", status = 400)
        
        except User.DoesNotExist:
            return HttpResponse("User not found", status = 404)
    return HttpResponse("Invalid Request Method", status=405)

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
            


            

