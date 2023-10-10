from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Locations(models.Model):
    locations = models.CharField(max_length=50)
    
    
class Services(models.Model):
    services = models.CharField(max_length=50)
    locations = models.ForeignKey(Locations,on_delete=models.CASCADE)
    image = models.ImageField(upload_to = 'media/service_images/',blank=True)



class CustomUser(AbstractUser):
    is_worker = models.BooleanField(default=False)
    phone = models.CharField(max_length=50,blank=True)
    # location = models.ForeignKey(Locations,on_delete=models.CASCADE)
    
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
    

# class WorkDetails(models.Model):
#     user = models.ForeignKey(CustomUser)
#     service = models.ForeignKey(Services)
#     worker = models.ForeignKey(CustomUser)
#     contact_details = models.TextField()
#     location = models.ForeignKey(Locations)
#     date = models.DateField(auto_now=True)
#     def __str__(self):
#         return f"{self.user}-{self.service}-{self.worker}"
    

class FielfOfExpertise(models.Model):
    worker = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    field = models.ForeignKey(Services,on_delete=models.CASCADE)
    
    
# class WorkerBookings(models.Model):
#     work_details = models.ForeignKey(WorkDetails,on_delete=models.CASCADE)
#     worker = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    
# class WorkerReview(models.Model):
#     worker = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
#     work_details = models.ForeignKey(WorkDetails)
#     comments = models.TextField()

class StoreOtp(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    otp = models.IntegerField()
    
class Otpstore(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    otp = models.IntegerField()