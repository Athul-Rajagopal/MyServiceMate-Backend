# serializers.py
from rest_framework import serializers

class BookingStatisticsSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    bookings = serializers.ListField(child=serializers.IntegerField())

class ServiceStatisticsSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    servicesCount = serializers.ListField(child=serializers.IntegerField())