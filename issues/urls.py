from django.urls import path
from . import views


urlpatterns = [
    path('create/', view=views.create_issue),
    path('all_issues/', view=views.get_all_issues),
    path('delete/<int:id>/', view=views.delete_issue)
]