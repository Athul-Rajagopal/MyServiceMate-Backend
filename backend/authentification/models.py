from django.db import models
from django.contrib.auth.models import AbstractUser

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
    
