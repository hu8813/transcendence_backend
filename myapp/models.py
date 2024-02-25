from django.db import models

# Create your models here.
class YourModel(models.Model):
    # your existing fields
    
    score = models.IntegerField(default=0) 