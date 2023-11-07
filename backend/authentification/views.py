from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializer import UserSerializers,LocationsSerializer, ServicesSerializer, ServiceLocationSerializer,BookingSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser,Locations, Services, Otpstore, ServiceLocation,WorkerDetails,FielfOfExpertise,Bookings,WorkerBookings
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
from math import radians, sin, cos, sqrt, atan2
from django.http import JsonResponse
from .signals import send_worker_notification
from django.contrib.auth.hashers import make_password




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


        
class ServicesByLocationList(APIView):
    def get(self,request,location_id):
        
        service_location = ServiceLocation.objects.filter(locations=location_id)
        data = []
        print(service_location)
        if service_location:
            for service_location in service_location:
            # Access the related service
                service = service_location.services

                # Prepare the data as a dictionary
                data_di = {
                    'id': service.id,
                    'services': service.services,
                    'image': service.image.url if service.image else None,
                }
                
                data.append(data_di)
                
                print(data)

        return Response(data)
        # else:
        #     return Response({'message': 'No services found for the selected location.'}, status=404)

    
    
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
        

class WorkerListingView(APIView):
    
    def post(self, request):
        selected_service = request.data.get("selectedService")
        selected_location = request.data.get("selectedLocation")
        
        print(selected_service,selected_location)
        
        service_obj = Services.objects.get(id=int(selected_service))
        workers = FielfOfExpertise.objects.filter(field=service_obj)
        
        location_obj = Locations.objects.get(id=int(selected_location))
        
        if location_obj:
            location_coords = (radians(location_obj.latitude), radians(location_obj.longitude))
            
            workers_in_range = []
            
            for worker_expertise in workers:
                worker = worker_expertise.worker  # Get the related worker
                worker_details = WorkerDetails.objects.get(worker=worker)
                worker_location_coords = (radians(worker_details.Location.latitude), radians(worker_details.Location.longitude))
                
                distance = self.calculate_haversine_distance(location_coords, worker_location_coords)
                
                if distance <= 15:  # Within 6 km range
                    workers_in_range.append({
                        'worker_id': worker.id,
                        'worker_name': worker.username,
                        'distance': distance,
                    })
            
            return JsonResponse(workers_in_range, safe=False)
        
        else:
            return JsonResponse([], safe=False)

    def calculate_haversine_distance(self, coords1, coords2):
        # Radius of the Earth in kilometers
        radius = 6371.0
        
        lat1, lon1 = coords1
        lat2, lon2 = coords2
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = radius * c
        return distance
    

class WorkerBookingsList(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        worker_id = self.kwargs['worker_id']  # Assumes the URL pattern has a parameter named 'worker_id'
        print(worker_id,type(worker_id))
        # try:
        worker = CustomUser.objects.get(id=worker_id)
        bookings = WorkerBookings.objects.filter(worker = worker).values('bookings')
        
        print(bookings)
        return Bookings.objects.filter(id__in=bookings)
        # except WorkerDetails.DoesNotExist:
        #     return []
    
class CreateBookings(generics.CreateAPIView):
    serializer_class = BookingSerializer
    queryset = Bookings
    
    def create(self,request,*args, **kwargs):
        
        user = self.request.user
        booking_date = request.data.get('date')
        user_address = request.data.get('address') 
        issue = request.data.get('issue')
        worker_id = request.data.get('workerId')
        
        # Convert ISO 8601 date to "YYYY-MM-DD" format
        formatted_date = datetime.fromisoformat(booking_date).strftime("%Y-%m-%d")
    
        booking = Bookings.objects.create(
            user=user,
            contact_address=user_address,
            issue=issue,
            date=formatted_date,
        )
        
        worker = CustomUser.objects.get(pk=worker_id)
        WorkerBookings.objects.create(worker=worker, bookings=booking)
        
        send_worker_notification(worker, booking)
        
        serializer = BookingSerializer(booking)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
class ListBookings(generics.ListAPIView):
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']  # Assumes the URL pattern has a parameter named 'worker_id'
        print(user_id,type(user_id))
        # try:
        user = CustomUser.objects.get(id=user_id)
        bookings = Bookings.objects.filter(user = user)
        
        print(bookings)
        return bookings
  
    
class ForgotPassword(APIView):
    
    def post(self,request):
        
        username = request.data.get('username')
        password = request.data.get('password')
        user_object = CustomUser.objects.get(username=username)
        
         # otp creation
        otp = get_random_string(length=4, allowed_chars='1234567890')
        expiry = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        stored_otp = Otpstore.objects.create(user=user_object, otp = otp)
    
        # otp sending via mail
        subject = 'OTP verification'
        message = f'Hello {username},\n\n' \
                    f'Please use the following OTP to reset your password: {otp}\n\n' \
                    f'Thank you!'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user_object.email]
        
        send_mail(subject, message, from_email, recipient_list)
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
    
class PasswordReset(APIView):
    
    def post(self,request):
        
        entered_otp = request.data.get('otp')
        entered_otp = int(entered_otp)
        username = request.data.get('username')
        password = request.data.get('password')
        user = CustomUser.objects.get(username=username)
        stored_otp = Otpstore.objects.get(user=user)
        
        if entered_otp == stored_otp.otp:
            # OTP is valid, proceed with user registration
            
            user.password = make_password(password)
            # Save the user
            user.save()
            
            # delete otp from db
            stored_otp.delete()
            return Response({'message': 'Registration successful','is_worker':user.is_worker}, status=status.HTTP_200_OK)
        else:
            # OTP is invalid
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)