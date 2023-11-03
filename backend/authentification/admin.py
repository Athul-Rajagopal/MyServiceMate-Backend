from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Locations)
admin.site.register(Services)
admin.site.register(CustomUser)
admin.site.register(WorkerDetails)
admin.site.register(FielfOfExpertise)
admin.site.register(ServiceLocation)
admin.site.register(Bookings)
admin.site.register(WorkerBookings)