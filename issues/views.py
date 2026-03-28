from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader
from .models import Issue
from users.models import User
import jwt
from django.conf import settings
SECRET_KEY=settings.SECRET_KEY
# Create your views here.

@csrf_exempt
def create_issue(req):
    if req.method == "POST":
            try:
                # token check
                token = req.COOKIES.get("token")
                if not token:
                    return JsonResponse({"error": "Not logged in"}, status=401)
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user = User.objects.get(id=payload["user_id"])

                #   data
                title = req.POST.get("title")
                category = req.POST.get("category")
                image_file=req.FILES.get("image")
                uploade_results = cloudinary.uploader.upload(image_file)
                image_url = uploade_results.get("secure_url")
                location = req.POST.get("location")
                description = req.POST.get("description")

                # create issue
                new_issue = Issue.objects.create(user=user,title=title, category=category, image=image_url, location=location, description=description)

                return JsonResponse({"message": "Issue created"}, status=201)
            
            except User.DoesNotExist:
                    return JsonResponse({"error": "User not found"}, status=404)

            except Exception as e:
                    return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


# get all issues
@csrf_exempt
def get_all_issues(req):
    issues = Issue.objects.all().values()
    list_issues = list(issues)

    return JsonResponse(list_issues, safe=False)

# delete issue
@csrf_exempt
def delete_issue(req, id):
    if req.method == "DELETE":
            try: 
                issue = Issue.objects.get(id=id)
                issue.delete()
                return JsonResponse({"message": "Issue deleted"}, status=200)
            
            except Issue.DoesNotExist:
                return JsonResponse({"error": "Issue not found"}, status=404)
    return JsonResponse({"error": "Issue not found"}, status=404)

# update issue
@csrf_exempt
def update_status(req):
    if req.method == "POST":
        issue_id = req.POST.get("id")
        status = req.POST.get("status")

        try:
            issue = Issue.objects.get(id=issue_id)
            issue.status=status
            issue.save()

            return JsonResponse({"message": "Status updated"})

        except Issue.DoesNotExist:
            return JsonResponse({"error": "Issue not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)



@csrf_exempt
def myIssues(req):
    try:
        # 🔐 get user from token
        token = req.COOKIES.get("token")
        if not token:
            return JsonResponse({"error": "Not logged in"}, status=401)

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=payload["user_id"])

        # 🎯 get user issues
        issues = Issue.objects.filter(user=user).values()

        return JsonResponse(list(issues), safe=False)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    except Exception as e:
        print("ERROR:", str(e))  # 🔥 check logs
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def make_admin(req):
    if req.method == "POST":
        email = req.POST.get("email")  # ✅ FormData support

        try:
            user = User.objects.get(email=email)
            user.is_admin = True
            user.save()

            return JsonResponse({"message": "User promoted to admin"})

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def view_admins(req):
    if req.method == "GET":
        admins = User.objects.filter(is_admin=True).values("id", "name", "email")

        return JsonResponse(list(admins), safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)