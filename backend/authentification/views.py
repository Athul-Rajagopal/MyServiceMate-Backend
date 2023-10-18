from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializer import UserSerializers,LocationsSerializer, ServicesSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser,Locations, Services, Otpstore
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from datetime import timedelta
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from backend import settings
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404




# Create your views here.


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        refresh = RefreshToken.for_user(user)
        access_token = str(response.data['access'])
        response.data['admin'] = user.is_superuser
        response.data['worker'] = user.is_worker
        response.data['username'] = user.username
        response.data['id'] = user.id
        response.data['access_token'] = access_token
        response.data['is_user'] = user.is_user
        response.data['is_approved'] = user.is_approved
        response.data['is_profile_created'] = user.is_profile_created
        response.data['is_active'] = user.is_active

        return response
    
    
class RegitrationView(APIView):
    
    def post(self, request):

        # if User.objects.filter(username=request.data['username']).exists():
        #     return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        # if User.objects.filter(email=request.data['email']).exists():
        #     return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        is_worker = serializer.validated_data.get('is_worker')
        
        print(username,email,password,is_worker)
     
        if serializer.is_valid():
            user = serializer.save()

            # otp creation
            otp = get_random_string(length=4, allowed_chars='1234567890')
            expiry = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
            user_object = get_object_or_404(CustomUser, username=user.username)
            stored_otp = Otpstore.objects.create(user=user_object, otp = otp)
        
            # otp sending via mail
            subject = 'OTP verification'
            message = f'Hello {username},\n\n' \
                        f'Please use the following OTP to verify your email: {otp}\n\n' \
                        f'Thank you!'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            
            send_mail(subject, message, from_email, recipient_list)
            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

    
class OTPVerificationView(APIView):
    def post(self, request):
        # Extract OTP entered by the user
        entered_otp = request.data.get('otp')
        entered_otp = int(entered_otp)
        username = request.data.get('user')

        # Retrieve the stored OTP from the session
        user = CustomUser.objects.get(username=username)
        stored_otp = Otpstore.objects.get(user=user)

        if entered_otp == stored_otp.otp:
            # OTP is valid, proceed with user registration
            
            user.is_active = True
            # Save the user
            user.save()
            
            # delete otp from db
            stored_otp.delete()
            return Response({'message': 'Registration successful','is_worker':user.is_worker}, status=status.HTTP_200_OK)
        else:
            # OTP is invalid
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        


class LocationsList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializer

class ServicesByLocationList(generics.ListAPIView):
    
    serializer_class = ServicesSerializer
    print(serializer_class)
    def get_queryset(self):
        location_id = self.kwargs['location_id']
        return Services.objects.filter(locations=location_id)
    # permission_classes = [IsAuthenticated]
    
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)

            # Add the token to the blacklist
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print("Error:", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
