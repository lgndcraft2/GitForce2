from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CustomUser
from rest_framework import status
from rest_framework import generics 
from .serializers import * 

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from twilio.twiml.messaging_response import MessagingResponse

from rest_framework.permissions import IsAuthenticated

# genai.configure(api_key=settings.GOOGLE_API_KEY)

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the userfiles index.")

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT token
        tokens = user.tokens()  # to create tokens method in model
        
        return Response({
            "message": "Login successful",
            "user": {
                "email": user.email,
            },
            "tokens": tokens
        }, status=status.HTTP_200_OK)

class RegisterView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) # this would always run all the methods in the serializer
        user = serializer.save()

        return Response({
            #"id": user.id,
            "message": "User registered successfully",
            "user": {
                "email": user.email,
            }
        }, status=status.HTTP_201_CREATED)

class SaveFileView(generics.CreateAPIView):
    queryset = SavedFile.objects.all()
    serializer_class = SavedFileSerializer
    permission_classes = [AllowAny] # User must be logged in

    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)

# Endpoint 2: Receive Data (GET)
class UserFilesListView(generics.ListAPIView):
    serializer_class = SavedFileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Return only the files belonging to the requesting user
        # .order_by('-timestamp') shows newest files first
        return SavedFile.objects.filter(user=self.request.user).order_by('-timestamp')

class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

class CreateFarmerView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

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

# 1. LIST (Get All) and CREATE (Post New)
class CropListCreateView(generics.ListCreateAPIView):
    queryset = SavedFile.objects.all().order_by('-timestamp')
    serializer_class = CropDataSerializer
    permission_classes = [AllowAny]  # 🔓 Open access

# 2. RETRIEVE (Get One), UPDATE (Put), and DESTROY (Delete)
class CropDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SavedFile.objects.all()
    serializer_class = CropDataSerializer
    permission_classes = [AllowAny]  # 🔓 Open access
'''
class AIAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] # Allows file uploads

    def post(self, request, *args, **kwargs):
        serializer = AIAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            # 1. Get the image from request
            image_file = request.FILES['image']
            
            # 2. Open image with Pillow so Gemini can read it
            img = Image.open(image_file)

            # 3. Define the Prompt for Gemini
            # We ask for JSON so we can easily parse it
            prompt = """
            Analyze this plant image. Identify the crop, detect any diseases or nutrient deficiencies.
            Return ONLY a raw JSON string (no markdown) with this format:
            {
                "crop_name": "Name of crop",
                "top_class": "Healthy or Name of Disease",
                "confidence": "Confidence percentage (e.g. 98%)",
                "recommendation": "Short advice"
            }
            """

            try:
                # 4. Call Gemini Model
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([prompt, img])
                
                # 5. Parse the AI Response
                import json
                # Clean up response text just in case Gemini adds ```json markdown
                cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
                ai_data = json.loads(cleaned_text)

                # 6. Save to Database
                # Note: We are saving the filename as 'file_data' to match your model
                saved_record = SavedFile.objects.create(
                    user=request.user,
                    # file_data=image_file.name, 
                    crop_name=ai_data.get('crop_name', 'Unknown'),
                    top_class=ai_data.get('top_class', 'Unknown'),
                    confidence=ai_data.get('confidence', '0%')
                )

                # 7. Return Result to Frontend
                return Response({
                    "message": "Analysis Complete",
                    "data": ai_data,
                    "record_id": saved_record.id
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

class FirebaseSyncView(generics.GenericAPIView):
    permission_classes = [AllowAny] # Public, because the user isn't in Django yet
    serializer_class = FirebaseUserSerializer

    def post(self, request):
        email = request.data.get('email')
        
        # 1. Validate that email was sent
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Check if user already exists
        # We use get_or_create. 
        # 'created' is a boolean (True if new user, False if existed)
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'username': email, # Use email as username since we don't have one
                'full_name': request.data.get('full_name', ''),
                'farm_location': request.data.get('farm_location', '')
            }
        )

        # 3. If it was a new user, we need to set an unusable password 
        # (Since they login via Firebase, they don't need a Django password)
        if created:
            user.set_unusable_password()
            user.save()
        
        # 4. Generate Django Tokens (So they can make authorized calls later)
        tokens = user.tokens()

        return Response({
            "message": "User synced successfully",
            "created": created, # Tells frontend if this was a new registration
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name
            },
            "tokens": tokens # <--- FRONTEND NEEDS THIS TO SAVE FILES
        }, status=status.HTTP_200_OK)