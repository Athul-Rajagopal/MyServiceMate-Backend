from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum

# Create your models here.

class Locations(models.Model):
    locations = models.CharField(max_length=50)
    latitude = models.FloatField(null=True,blank=True)
    longitude = models.FloatField(null=True,blank=True)
    
    def __str__(self):
        return self.locations
    
    
class Services(models.Model):
    services = models.CharField(max_length=50)
    image = models.ImageField(upload_to = 'media/service_images/',blank=True)

class ServiceLocation(models.Model):
    services = models.ForeignKey(Services, on_delete=models.CASCADE)
    locations = models.ForeignKey(Locations, on_delete=models.CASCADE)

class CustomUser(AbstractUser):
    is_worker = models.BooleanField(default=False)
    phone = models.CharField(max_length=50,blank=True)
    is_approved = models.BooleanField(default=False)
    is_user = models.BooleanField(default=True)
    is_profile_created = models.BooleanField(default=False)
    
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='custom_users_groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='custom_users_permissions'
    )

    def __str__(self):
        return f"{self.username}-{self.email}"
    
    
class Bookings(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    contact_address = models.TextField()
    issue = models.TextField()
    date = models.DateField()
    is_accepted = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user}-{self.date}'
    
    
class WorkerDetails(models.Model):
    worker = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    Location = models.ForeignKey(Locations,on_delete=models.CASCADE)
    phone = models.CharField(max_length=12,null=True)
    join_date = models.DateField(auto_now=True,blank=True,null=True)
    
class WorkerBookings(models.Model):
    worker = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    bookings = models.ForeignKey(Bookings,on_delete=models.CASCADE)
    
    

class FielfOfExpertise(models.Model):
    worker = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    field = models.ForeignKey(Services,on_delete=models.CASCADE)
    


    
class Otpstore(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    otp = models.IntegerField()
    
    
class Review(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    comment = models.TextField()
    date = models.DateField(auto_now=True)
    
class WorkerReview(models.Model):
    worker = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    reviews = models.ForeignKey(Review,on_delete=models.CASCADE)
    
    
class Payment(models.Model):
    Bookings = models.ForeignKey(Bookings, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True, blank=True , null=True)
    payed_date_time = models.DateTimeField(blank=True , null=True)
    received_date_time = models.DateTimeField(blank=True , null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments_as_user')
    worker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments_as_worker')
    is_recieved = models.BooleanField(default=False)  # Add the payment status field
    is_payed = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=50, blank=True,null=True)  # Add the payment ID field

    def _str_(self):
        return f"Payment for booking ID {self.Bookings.bookings.id} by {self.user.username}"


class WorkerWallet(models.Model):
    Worker = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    wallet_amount = models.IntegerField()
    
    def __str__(self):
        return f"{self.Worker.username}-{self.wallet_amount}"
   
    
class AdminWallet(models.Model):
    date = models.DateTimeField(auto_now=True, blank=True, null=True)
    wallet_amount = models.IntegerField()
    
    @classmethod
    def get_total_wallet_amount(cls):
        # Calculate and return the total wallet amount
        total_amount = cls.objects.aggregate(Sum('wallet_amount'))['wallet_amount__sum']
        return total_amount if total_amount is not None else 0
    
    def __str__(self):
        return f"-{self.wallet_amount}"