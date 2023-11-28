from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializer import UserSerializers,LocationsSerializer, ServicesSerializer, ServiceLocationSerializer,BookingSerializer,ReviewSerializer,PaymentSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser,Locations, Services, Otpstore, ServiceLocation,WorkerDetails,FielfOfExpertise,Bookings,WorkerBookings,Review,WorkerReview,Payment,WorkerWallet,AdminWallet
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
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.utils import timezone



# Create your views here.
#Registration

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
        

            return Response(data)
        else:
            return Response({'message': 'No services found for the selected location.'}, status=404)

#Logout    
    
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
            
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
#Worker listing
class WorkerListingView(APIView):
    
    def post(self, request):
        selected_service = request.data.get("selectedService")
        selected_location = request.data.get("selectedLocation")
        
        print('selected service',selected_service,'selected location',selected_location)
        
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
            print(workers_in_range)
            
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
    
#Booking

class WorkerBookingsList(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        worker_id = self.kwargs['worker_id']  # Assumes the URL pattern has a parameter named 'worker_id'
        
        # try:
        worker = CustomUser.objects.get(id=worker_id)
        bookings = WorkerBookings.objects.filter(worker = worker).values('bookings')
        
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
        
        # Remove milliseconds from the ISO 8601 date string
        booking_date_without_ms = booking_date.rsplit('.', 1)[0]
        
        # Convert ISO 8601 date to "YYYY-MM-DD" format
        formatted_date = datetime.fromisoformat(booking_date_without_ms).strftime("%Y-%m-%d")
    
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
       
        # try:
        user = CustomUser.objects.get(id=user_id)
        bookings = Bookings.objects.filter(user = user)
        
        return bookings

#Password  
    
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
        
#Review 

class IsAllowedToAddReview(APIView):
    def post(self,request):
        
        user_id = request.data.get('user_id')
        worker_id = request.data.get('worker_id')
        
        worker = CustomUser.objects.get(id=worker_id)
        user = CustomUser.objects.get(id=user_id)
        
        bookings = WorkerBookings.objects.filter(worker = worker).values('bookings')
        user_worker_relation = Bookings.objects.filter(id__in=bookings, user=user)
        
        if user_worker_relation:
            return Response({'message': 'valid for giving reviews'},status=status.HTTP_200_OK)
        else:
            return Response({'error':'Not have a single booking'},status=status.HTTP_400_BAD_REQUEST)
        
class AddReview(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review

    def create(self, request, *args, **kwargs):
        user = self.request.user
        worker_id = request.data.get('worker_id')
        comment = request.data.get('comment')

        review = Review.objects.create(
            user=user,
            comment=comment,
        )

        worker = CustomUser.objects.get(pk=worker_id)
        WorkerReview.objects.create(worker=worker, reviews=review)
        # Instantiate the serializer with the created review object
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class GetPendingPayments(generics.ListAPIView):
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        
       user_id = self.kwargs['user_id'] 
       user = CustomUser.objects.get(id=user_id)
       pending_payments = Payment.objects.filter(user=user,is_recieved=False,is_payed=False)
       
       return pending_payments

class GetPaymentHistory(generics.ListAPIView):
       
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        
       user_id = self.kwargs['user_id'] 
       user = CustomUser.objects.get(id=user_id)
       payment_history = Payment.objects.filter(user=user,is_payed=True)
       
       return payment_history
   
class StripeCheckoutView(APIView):
    def post(self, request):
        user = request.user      
        worker_username = request.data['payment']['worker']['username']
        booking_details = request.data['payment']['Bookings']
        booking_id = request.data['payment']['Bookings']['id']
        Total_amount = request.data['payment']['amount']
        print(worker_username,booking_details,booking_id,Total_amount)
        print('requests strip checking')
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            # Ensure that course.price is an integer representing the price in cents.
            pricess = int(float(Total_amount) * 100)           
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'unit_amount': pricess,
                            'product_data': {
                                'name': user.username,
                            },
                        },
                        'quantity': 1,
                    },
                ],
                payment_method_types=['card'],
                mode='payment',
                metadata = {
                    'userId': user.id,
                    'worker': worker_username,
                    'BookingId': booking_id,
                    'amount' : Total_amount,
                },
                success_url=settings.SITE_URL + f'/?success=true&session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=settings.SITE_URL + '/?canceled=true',
            )
            # print(checkout_session.url)
            # Return a valid JsonResponse
            return JsonResponse({'session_id': checkout_session.id})

        except stripe.error.StripeError as e:
            # Handle Stripe-specific errors
            # print(f"Stripe Error: {e}")
            return Response(
                {
                    'error': 'Something went wrong when creating the Stripe checkout session'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # Handle other exceptions
            # print(f"An error occurred: {e}")
            return Response(
                {
                    'error': 'An error occurred while processing the request'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
  
 
@csrf_exempt 
def stripe_webhook_view(request):
    print('#############################################')
    payload = request.body
    endpoint = settings.STRIPE_WEBHOOK_SECRET
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
        event['data']['object']['id'],
        expand=['line_items'],
        )
        
        # print(session)
        booking_id = session['metadata']['BookingId']
        worker_name = session['metadata']['worker']
        user_id = session['metadata']['userId']
        amount = session['metadata']['amount']
        payment_id = session.line_items.data[0]['id']
        # print('payment_id .............>>',payment_id)
        user = CustomUser.objects.get(id=int(user_id))
        booking = Bookings.objects.get(id=int(booking_id))
        
        payment_obj = Payment.objects.get(
            Bookings = booking,
            amount = float(amount),
            user = user
        )
        
        payment_obj.is_recieved = True
        payment_obj.is_payed = True
        payment_obj.payed_date_time = timezone.now()
        payment_obj.received_date_time = timezone.now()
        payment_obj.payment_id = payment_id
        payment_obj.save()
        
        wallet_amount = float(amount)-50
        worker_wallet = WorkerWallet.objects.create(Worker = payment_obj.worker, wallet_amount = wallet_amount)
        worker_wallet.save()
        
        # admin = CustomUser.objects.get(is_superuser=True)
        date = timezone.now()
        admin_wallet = AdminWallet.objects.create(date=date, wallet_amount=50)
        admin_wallet.save()

    # Passed signature verification
    return HttpResponse(status=200)

