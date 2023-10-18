from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from .views import *

urlpatterns = [
    path('select-service/', ServiceList.as_view(), name = 'select_service'),
    path('update-worker-location/', WorkerLocationUpdateView.as_view(), name='update_worker_location'),
    path('set-field-of-expertice/',SetFieldOfExpertice.as_view(), name='set_field_of_expertice'),
    path('edit-phone-number/',EditWorkerPhoneNumber.as_view(), name='edit_phone_number'),
    path('worker-profile/', ViewWorkerProfile.as_view(), name='worker_profile'),

]