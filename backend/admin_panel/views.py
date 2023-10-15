from django.shortcuts import render
from authentification.serializer import UserSerializers
from authentification.models import Services,WorkerDetails,CustomUser,FielfOfExpertise,Locations
from authentification.serializer import UserSerializers,WorkerDetailsSerializer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from rest_framework import status
from django.http import JsonResponse
# Create your views here.

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

        
        # except Exception as e:
        #     # Handle exceptions, e.g., user not found, data not found, etc.
        #     return JsonResponse({'error': str(e)}, status=500)
            
        
        
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
        
        