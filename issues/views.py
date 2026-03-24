from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader
from .models import Issue
from users.models import User
# Create your views here.

@csrf_exempt
def create_issue(req):
    if req.method == "POST":
            title = req.POST.get("title")
            category = req.POST.get("category")
            image_file=req.FILES.get("image")
            uploade_results = cloudinary.uploader.upload(image_file)
            image_url = uploade_results.get("secure_url")
            location = req.POST.get("location")
            description = req.POST.get("description")
            email = req.POST.get("email")

            try:
                  user = User.objects.get(email=email)   # find user by emial

                  new_issue = Issue.objects.create(user=user,title=title, category=category, image=image_url, location=location, description=description)

                  return HttpResponse("Issue created", status=201)
            except User.DoesNotExist:
                return HttpResponse("User not found", status = 404)
    return HttpResponse("Invalid request", status=400)


# get all issues
@csrf_exempt
def get_all_issues(req):
    issues = Issue.objects.all().values()
    list_issues = list(issues)
    if list_issues == []:
        return JsonResponse({"message": "No issues found"}, status=200)
    
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
