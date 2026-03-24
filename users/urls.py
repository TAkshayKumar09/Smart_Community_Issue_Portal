from django.urls import path
from . import views



urlpatterns =[
    path('register/', view=views.register ),
    path('login/', view=views.login),
    path('userdetails/<str:email>/', view=views.get_profile)
]