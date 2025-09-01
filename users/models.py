from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    email = models.EmailField(max_length=254)
    profile_image = models.URLField(max_length=500, blank=True)