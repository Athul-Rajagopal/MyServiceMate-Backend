from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework import serializers
from .models import CustomUser,Locations,Services

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'is_worker', 'phone']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password) 
        instance.save()
        return instance
    


class LocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locations
        fields = '__all__'

class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'
    