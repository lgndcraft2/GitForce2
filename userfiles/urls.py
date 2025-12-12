from django.urls import path, include
from .views import UserProfileView
from .views import WhatsAppBotView, index, CreateFarmerView, UserProfileView

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', index, name='index'),
    path('', UserProfileView.as_view(), name='send_info'),  
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('whatsapp/', WhatsAppBotView.as_view(), name='whatsapp-bot'),
    path('farmer/onboard/', CreateFarmerView.as_view(), name='farmer-onboard'),
]
