from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser
from rest_framework import status
from rest_framework import generics 
from .serializers import CustomUserSerializer 

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from twilio.twiml.messaging_response import MessagingResponse

from rest_framework.permissions import IsAuthenticated

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the userfiles index.")

class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        GET user profile by Firebase UID passed in query params
        Example: /sendinfo/?uid=abc123
        """
        uid = request.query_params.get('uid')
        if not uid:
            return Response({"error": "UID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(uid=uid)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        POST user profile by Firebase UID in JSON body
        """
        uid = request.data.get('uid')
        if not uid:
            return Response({"error": "UID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(uid=uid)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user)
        return Response(serializer.data)


class CreateFarmerView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Save user normally; no .user foreign key needed
        serializer.save()

class WhatsAppBotView(APIView):
    # Twilio sends data as form-encoded, so we need these parsers
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [AllowAny] # Allow Twilio to hit this endpoint without a token

    def post(self, request, *args, **kwargs):
        # 1. Get the data from the request
        incoming_msg = request.data.get('Body', '').strip()
        num_media = request.data.get('NumMedia', '0') # Comes as a string
        sender_number = request.data.get('From')
        
        # 2. Initialize Twilio Response Object
        resp = MessagingResponse()
        msg = resp.message()

        print(f"📩 Message received from {sender_number}")

        # 3. Logic: Check if they sent an image
        if int(num_media) > 0:
            image_url = request.data.get('MediaUrl0')
            
            # --- MOCK AI ANALYSIS START ---
            # In a real scenario, you'd pass 'image_url' to your ML model function here
            print(f"🖼 Analyzing Image: {image_url}")
            
            grade = "Grade A"
            price = "₦12,000"
            token_value = "50 AGRI"
            # --- MOCK AI ANALYSIS END ---

            # 4. Construct the Reply
            reply_text = (
                f"🍅 *AgriTrust Analysis*\n"
                f"----------------\n"
                f"✅ *Quality:* {grade}\n"
                f"💰 *Est. Price:* {price}\n"
                f"----------------\n"
                f"Tap below to mint & sell on Blockchain: 👇\n"
                f"https://your-webapp.com/mint?grade=A&price=12000"
            )
            msg.body(reply_text)
            
        else:
            # Welcome Message (Text only)
            msg.body(
                "👋 Welcome to *AgriTrust Nigeria*!\n\n"
                "Please send a photo 📸 of your crop to get an instant AI valuation."
            )

        # 5. Return XML (Critical for Twilio)
        # We use standard HttpResponse because DRF's Response() returns JSON
        return HttpResponse(str(resp), content_type='text/xml')