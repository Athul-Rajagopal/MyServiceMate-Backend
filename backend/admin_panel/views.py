from django.shortcuts import render
from authentification.serializer import UserSerializers
from authentification.models import Services,WorkerDetails,CustomUser,FielfOfExpertise,Locations,WorkerBookings,Bookings,Payment,AdminWallet
from authentification.serializer import UserSerializers,WorkerDetailsSerializer,ServicesSerializer,LocationsSerializer,BookingSerializer,PaymentSerializer,AdminWalletSerializer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework import status
from django.http import JsonResponse
from .serializers import BookingStatisticsSerializer,ServiceStatisticsSerializer
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from django.db.models import Count
from django.utils import timezone
# Create your views here.

# worker management

class WorkerApprovalRequestListView(APIView):
    def get(self, request):
        approval_requests = CustomUser.objects.filter(is_worker=True, is_approved=False)
        serialized_data = []

        for data in approval_requests:
            try:
                worker_details = WorkerDetails.objects.get(worker=data)
                field_of_expertise = FielfOfExpertise.objects.filter(worker=data)
                location = Locations.objects.get(id=worker_details.Location.id)

                # Assuming you have serializers for these models
                serialized_data.append({
                    'id': data.id,
                    'username': data.username,
                    'phone': worker_details.phone,
                    'location': location.locations,
                    'expertise': [{'services': field.field.services, 'id': field.field.id} for field in field_of_expertise],
                })
            except WorkerDetails.DoesNotExist:
                serialized_data.append({
                    'id': data.id,
                    'username': data.username,
                    'phone': 'Not provided',
                    "location": 'Not provided',
                    'expertise': [{'services': 'not selected', 'id': 'unknown'}]
                })

        print(serialized_data)

        return JsonResponse({'data': serialized_data}, safe=False)

            
class PendingApprovalRequestCount(APIView):
    def get(self,request):  
        approval_requests = CustomUser.objects.filter(is_worker=True, is_approved=False).count()
        return Response({'count': approval_requests})    
        
class WorkerApprovalView(APIView):
    def patch(self, request, worker_id):
        try:
            worker = CustomUser.objects.get(id=int(worker_id), is_worker=True, is_approved=False)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Worker not found or has already been approved"},
                status=status.HTTP_NOT_FOUND
            )

        # Update the worker's 'is_approved' field to True
        worker.is_approved = True
        worker.save()

        return Response(
            {"message": "Worker approved successfully"},
            status=status.HTTP_200_OK
        )
        
class GetWorkersList(APIView):
    def get(self, request):
        approval_requests = CustomUser.objects.filter(is_worker=True, is_approved=True)
        serialized_data = []

        for data in approval_requests:
            try:
                worker_details = WorkerDetails.objects.get(worker=data)
                field_of_expertise = FielfOfExpertise.objects.filter(worker=data)
                location = Locations.objects.get(id=worker_details.Location.id)

                # Assuming you have serializers for these models
                serialized_data.append({
                    'id': data.id,
                    'username': data.username,
                    'is_active': data.is_active,
                    'phone': worker_details.phone,
                    'location': location.locations,
                    'expertise': [{'services': field.field.services, 'id': field.field.id} for field in field_of_expertise],
                })
            except WorkerDetails.DoesNotExist:
                serialized_data.append({
                    'id': data.id,
                    'username': data.username,
                    'is_active': data.is_active,
                    'phone': 'Not provided',
                    "location": 'Not provided',
                    'expertise': [{'services': 'not selected', 'id': 'unknown'}]
                })


        return JsonResponse({'data': serialized_data}, safe=False)
        
# service management
       
class ServiceCreateView(generics.CreateAPIView):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer

    def create(self, request, *args, **kwargs):
        # Deserialize the data using the serializer
        print('request.data ===',request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create a new service
        service = serializer.save()

        # Add selected locations to the service
        location_ids = request.data.get('location[]',[])
        print(location_ids)
        for location_id in location_ids:
            location = Locations.objects.get(id = int(location_id))
            serviceLocation = ServiceLocation.objects.create(services=service, locations=location)
            serviceLocation.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
     
class ServiceDeleteView(generics.DestroyAPIView):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)   


# Location management

class LocationCreateView(generics.CreateAPIView):
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
class RemoveLocationView(generics.DestroyAPIView):
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializer
    
    
# user management

class GetuserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializers
    
    
class BlockUnblockUsers(APIView):
 
    def put(self, request,username):
        user = CustomUser.objects.get(username=username)
        if user.is_active:
            user.is_active = False  # Set is_active to False when blocking
        else:
            user.is_active = True
        user.save()
        serializer = UserSerializers(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# Booking management

class WorkerBookingsList(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        worker_id = self.kwargs['worker_id']
        # Filter bookings by worker_id and is_accepted status
        worker = CustomUser.objects.get(id=worker_id)
        bookings = WorkerBookings.objects.filter(worker = worker).values('bookings')
        return Bookings.objects.filter(id__in=bookings)



class UserBookingsList(generics.ListAPIView):
    serializer_class = BookingSerializer

    def get_queryset(self):
        user_name = self.kwargs['user_name']
        user = CustomUser.objects.get(username=user_name)
        booking_ids = Bookings.objects.filter(user=user).values_list('id', flat=True)
        worker_bookings = WorkerBookings.objects.filter(bookings__in=booking_ids)
        worker_ids = worker_bookings.values_list('worker', flat=True).distinct()
        bookings = Bookings.objects.filter(id__in=booking_ids)
        return bookings

    def get_worker_names(self, queryset):
        booking_ids = [booking['id'] for booking in queryset.values('id')]
        worker_bookings = WorkerBookings.objects.filter(bookings__in=booking_ids)
        worker_ids = worker_bookings.values_list('worker', flat=True).distinct()
        worker_names = {}
        for worker_booking in worker_bookings:
            worker_names[worker_booking.bookings.id] = worker_booking.worker.username
        return [worker_names.get(booking_id) for booking_id in booking_ids]
    
    
# Dashboard

@api_view(['GET'])
def booking_statistics(request):
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    start_date = None
    end_date = None

    if from_date and to_date:
        # If both from_date and to_date are provided, filter by the specified date range
        data = Bookings.objects.filter(date__range=[from_date, to_date])
        start_date = datetime.strptime(from_date, '%Y-%m-%d')
        end_date = datetime.strptime(to_date, '%Y-%m-%d') + timedelta(days=1)
    else:
        # If no dates are provided, use the last 7 days as a default
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        data = Bookings.objects.filter(date__range=[start_date, end_date])

    # Get the count of bookings for each day in the date range
    date_range = [start_date + timedelta(days=x) for x in range(7)]
    booking_counts = [data.filter(date=date).count() for date in date_range]

    data = {
        'labels': [date.strftime('%Y-%m-%d') for date in date_range],
        'bookings': booking_counts,
    }

    serializer = BookingStatisticsSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
def service_statistics(request):
    # Query your Services model to get service statistics
    data = Services.objects.annotate(booking_count=Count('servicelocation__services'))
    labels = [entry.services for entry in data]
    servicesCount = [entry.booking_count for entry in data]

    serializer = ServiceStatisticsSerializer(data={'labels': labels, 'servicesCount': servicesCount})
    if serializer.is_valid():
        return Response(serializer.validated_data)
    return Response(serializer.errors, status=400)


class Transactions(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    
class AdminWalletView(generics.ListAPIView):
    serializer_class = AdminWalletSerializer
    queryset = AdminWallet.objects.all()

    def get_serializer_context(self):
        # Pass the total_wallet_amount to the serializer context
        total_wallet_amount = AdminWallet.get_total_wallet_amount()
        return {'total_wallet_amount': total_wallet_amount}