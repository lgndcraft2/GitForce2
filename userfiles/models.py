from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    uid = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=30)
    farm_location = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    

class SavedFile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    confidence = models.CharField(max_length=255)
    crop_name = models.CharField(max_length=255)
    top_class = models.CharField(max_length=255)
    file_data = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} uploaded by {self.user.username}"