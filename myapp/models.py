from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    score = models.IntegerField(default=0)

#class Tournament(models.Model):
#    name = models.CharField(max_length=100)
#    start_date = models.DateField()