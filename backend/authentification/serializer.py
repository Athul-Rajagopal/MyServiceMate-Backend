from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework import serializers
from .models import CustomUser,Locations,Services,WorkerDetails,FielfOfExpertise,ServiceLocation,Bookings



class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'is_worker', 'phone', 'is_active', 'is_superuser','is_approved','is_user','is_profile_created']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data['is_active'] = False
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
        
        
class ServiceLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLocation
        fields = '__all__'
        
        

# worker details      
class WorkerDetailsSerializer(serializers.ModelSerializer):
    Location = LocationsSerializer()
    services = ServicesSerializer(many=True)

    class Meta:
        model = WorkerDetails
        fields = ('phone', 'Location', 'services')
  
  
class BookingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Bookings
        fields = ['id', 'user', 'username','contact_address', 'issue', 'date', 'is_accepted','is_completed','is_rejected',]


        
class WorkerDetailsUpdateLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerDetails
        fields = ['Location']
        
class FieldOfExperticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FielfOfExpertise
        fields = '__all__'
        
class WorkerDetailsUpdatePhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerDetails
        fields = ['phone']
    
