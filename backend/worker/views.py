from django.shortcuts import render
from authentification.serializer import ServicesSerializer,FieldOfExperticeSerializer,WorkerDetailsUpdateLocationSerializer,WorkerDetailsUpdatePhoneNumberSerializer
from authentification.models import Services,WorkerDetails,CustomUser,FielfOfExpertise,Locations
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework import status
from django.http import JsonResponse


# Create your views here.


class ServiceList(generics.ListAPIView):
    
    queryset = Services.objects.all()
    print(queryset)
    serializer_class = ServicesSerializer
    
class WorkerLocationUpdateView(generics.CreateAPIView):
    queryset = WorkerDetails.objects.all()
    serializer_class = WorkerDetailsUpdateLocationSerializer

    def create(self, request, *args, **kwargs):
        permission_classes = [IsAuthenticated]
        user = self.request.user
        new_location = int(request.data.get('Location'))

        # Check if a WorkerDetails instance with the same worker and Location exists
        worker_details = WorkerDetails.objects.filter(worker=user, Location=new_location).first()

        if worker_details:
            # If an instance already exists, you might want to update it instead of creating a new one
            # Update worker_details here
            serializer = self.get_serializer(worker_details)
        else:
            # Create a new WorkerDetails instance with the worker and location
            location = get_object_or_404(Locations, id=new_location)
            worker_details = WorkerDetails.objects.create(worker=user, Location=location)

            # Serialize the newly created instance
            serializer = self.get_serializer(worker_details)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
class SetFieldOfExpertice(generics.ListCreateAPIView):
    queryset = FielfOfExpertise.objects.all()
    serializer_class = FieldOfExperticeSerializer
    
    def create(self, request, *args, **kwargs):
        # Retrieve the worker (user) from the request, assuming the worker is the authenticated user
        worker = request.user  # The authenticated user

        # Retrieve the selected fields from the request data
        selected_fields = request.data.get('fields', [])  # Assuming the selected fields are sent as a list of field IDs
        
        print(worker, selected_fields)

        # Create FieldOfExpertise instances for each selected field and associate them with the worker
        field_instances = []
        for field_id in selected_fields:
            # try:
            field_id = int(field_id)
            field = Services.objects.get(id=field_id)
            existing_expertise = FielfOfExpertise.objects.filter(worker=worker, field=field)
            if not existing_expertise:
                    field_of_expertise = FielfOfExpertise(worker=worker, field=field)
                    field_of_expertise.save()
                    field_instances.append(field_of_expertise)
            else:
                return Response(status=status.HTTP_409_CONFLICT)
            
            # except Service.DoesNotExist:
                # Handle the case where the selected field doesn't exist
                # pass

        # Serialize and return the created FieldOfExpertise instances
        serializer = FieldOfExperticeSerializer(field_instances, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class EditWorkerPhoneNumber(generics.UpdateAPIView):
    queryset = WorkerDetails.objects.all()
    serializer_class = WorkerDetailsUpdatePhoneNumberSerializer
    
    def partial_update(self, request, *args, **kwargs):
        # Get the user making the request
        worker = self.request.user

        # Get the new location from the request data
        Phone = request.data.get('phone')

        # Find the WorkerDetails object for the user
        worker_details = WorkerDetails.objects.get(worker=worker)

        # Update the location
        worker_details.phone = Phone
        worker_details.save()
        
        worker.is_profile_created = True
        worker.save()

        return Response({'message': 'Location updated successfully'}, status=status.HTTP_200_OK)
 
    
class ViewWorkerProfile(APIView):
    
    def get(self,request):
       
        serialized_data = []
        worker_details = WorkerDetails.objects.get(worker=request.user)
        field_of_expertise = FielfOfExpertise.objects.filter(worker=request.user)
        location = Locations.objects.get(id=worker_details.Location.id)
        
        serialized_data.append({
                        'id':request.user.id,
                        'username': request.user.username,
                        'phone': worker_details.phone,
                        'location': location.locations,
                        'expertise': [{'services':field.field.services,
                                       'id':field.field.id,
                                       'image':field.field.image.url} for field in field_of_expertise],
                    })
        
        print(serialized_data)

        return JsonResponse({'data': serialized_data}, safe=False)