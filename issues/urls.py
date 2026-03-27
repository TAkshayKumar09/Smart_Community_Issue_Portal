from django.urls import path
from . import views


urlpatterns = [
    path('create_issue/', view=views.create_issue),
    path('all_issues/', view=views.get_all_issues),
    path('delete_issue/<int:id>/', view=views.delete_issue),
    path('update_issue/', view=views.update_status)
]