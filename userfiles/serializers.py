from rest_framework import serializers
from .models import CustomUser, SavedFile

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['uid', 'full_name', 'email', 'phone', 'farm_location']    

class SavedFileSerailizer(serializers.ModelSerializer):
    class Meta:
        model = SavedFile
        fields = ['user', 'confidence', 'crop_name', 'top_class', 'file_data', 'timestamp']