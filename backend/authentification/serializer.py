from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework import serializers
from .models import CustomUser,Locations,Services,WorkerDetails,FielfOfExpertise,ServiceLocation,Bookings,WorkerBookings,Review,WorkerReview,Payment,WorkerWallet,AdminWallet



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
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    
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
    worker_name = serializers.SerializerMethodField()
    class Meta:
        model = Bookings
        fields = ['id', 'user', 'username','contact_address', 'issue', 'date', 'is_accepted','is_completed','is_rejected','worker_name']
        
    def get_worker_name(self, obj):
        # Retrieve the worker's name associated with the booking
        worker_booking = WorkerBookings.objects.get(bookings=obj)
        worker_name = worker_booking.worker.username
        return worker_name


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    worker_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'user', 'comment', 'date', 'username', 'worker_name']
        
    def get_worker_name(self, obj):
        # Retrieve the worker's name associated with the review
        worker_review = WorkerReview.objects.get(reviews=obj)
        worker_name = worker_review.worker.username
        return worker_name


        
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
    


class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializers()
    worker = UserSerializers()
    Bookings = BookingSerializer()

    class Meta:
        model = Payment
        fields = '__all__'
        
class WalletSerializer(serializers.ModelSerializer):
    Worker = UserSerializers()
    class Meta:
        model = WorkerWallet
        fields = '__all__'
        
class AdminWalletSerializer(serializers.ModelSerializer):
    total_wallet_amount = serializers.SerializerMethodField()

    class Meta:
        model = AdminWallet
        fields = '__all__'

    def get_total_wallet_amount(self, obj):
        # Call the get_total_wallet_amount method from the model
        return AdminWallet.get_total_wallet_amount()

class walletWithdrawalSerializer(serializers.ModelSerializer):
    worker = UserSerializers()
    class Meta:
        model = WalletWithdrawRequest
        fields = '__all__'
