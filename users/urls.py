from django.urls import path
from . import views



urlpatterns =[
    path('register/', view=views.register ),
    path('login/', view=views.login),
    path('userdetails/', view=views.get_user),
    path('updatedetails/', view=views.update_user)
]