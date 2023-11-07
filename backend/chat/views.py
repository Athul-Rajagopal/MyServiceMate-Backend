from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Message
from .serializer import MessageSerializer
from authentification.models import CustomUser
from authentification.serializer import UserSerializers

from django.db import models

# Create your views here.


class MessageCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UserWorkerChatView(APIView):
    def get(self,request,user_id,worker_id,*args,**kwargs):
        try:
            user_profile=CustomUser.objects.get(id=user_id)
            worker_profile=CustomUser.objects.get(id=worker_id)
        except CustomUser.DoesNotExist:
            return Response({"error":"invalid user or doctor"}, status=status.HTTP_400_BAD_REQUEST)
        # Fetch all messages related to the user and doctor
        messages=Message.objects.filter(
            (models.Q(sender=user_profile)&models.Q(receiver=worker_profile)) |
            (models.Q(sender=worker_profile)&models.Q(receiver=user_profile))

        ).order_by('timestamp')

        serializer=MessageSerializer(messages,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
class GetUserData(APIView):
    
    def get(self, request, id):
        try:
            user_data = CustomUser.objects.get(id=id)
            serializer = UserSerializers(user_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_NOT_FOUND)
        

class WorkerChatView(APIView):
    def get(self, request,id, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # Retrieve distinct combinations of sender and receiver IDs from Message model
        users_chatted_with = Message.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user)
        ).exclude(sender=user).values('sender', 'receiver').distinct()

        # Extract unique user IDs from the combinations
        user_ids = set()
        for chat in users_chatted_with:
            user_ids.add(chat['sender'])
            user_ids.add(chat['receiver'])

        # Remove the current user's ID from the set
        user_ids.discard(user.id)

        users = CustomUser.objects.filter(id__in=user_ids)

        # Serialize the list of users along with their IDs
        serializer = UserSerializers(users, many=True)

        # Create a list of dictionaries with user IDs and user data
        chatted_users_data = [{'id': user.id, 'data': user_data} for user, user_data in zip(users, serializer.data)]

        return Response(chatted_users_data, status=200)