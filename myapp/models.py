from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    score = models.IntegerField(default=0)
    
# Create your models here.
class YourModel(models.Model):
    # your existing fields
    
    score = models.IntegerField(default=0) 