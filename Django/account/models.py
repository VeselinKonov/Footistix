from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django import forms

MAX_LENGTH = 255
class User(AbstractUser):
    email       = models.EmailField(unique=True)
    username    = models.CharField(unique=True, max_length=MAX_LENGTH)
    is_active   = models.BooleanField(default=False)
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    