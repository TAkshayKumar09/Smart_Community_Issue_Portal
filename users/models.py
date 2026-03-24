from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=100,)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    is_admin = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.email

from users.models import User

user = User.objects.get(email="akshay@gmail.com")
user.is_admin = True
user.save()