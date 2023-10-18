from django.shortcuts import render
from authentification.serializer import UserSerializers
from authentification.models import Services,WorkerDetails,CustomUser,FielfOfExpertise,Locations
from authentification.serializer import UserSerializers,WorkerDetailsSerializer,ServicesSerializer,LocationsSerializer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework import status
from django.http import JsonResponse
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

        print(serialized_data)

        return JsonResponse({'data': serialized_data}, safe=False)
        
# service management
       
class ServiceCreateView(generics.CreateAPIView):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer

    def create(self, request, *args, **kwargs):
        services = request.data.get('services')
        location_id = request.data.get('location')
        image = request.data.get('image')

        # Check if the location exists
        print(request.data)
        try:
            location = Locations.objects.get(id=location_id)
        except Locations.DoesNotExist:
            return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create a new Services object
        service = Services(services=services, locations=location, image=image)
        service.save()

        return Response({'message': 'Service created successfully'}, status=status.HTTP_201_CREATED)
    
     
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
