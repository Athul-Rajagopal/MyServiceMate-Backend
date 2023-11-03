from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from .views import *

urlpatterns = [
    path('signup/',RegitrationView.as_view(), name='signup'),
    path('otp-verification',OTPVerificationView.as_view(), name='otp_verification'),
    path('token/', CustomTokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),    
    path('locations/', LocationsList.as_view(), name='locations-list'),
    path('services/<int:location_id>/', ServicesByLocationList.as_view(), name='services-by-location'),
    path('signout/',LogoutView.as_view(), name='signout'),
    path('worker-list/',WorkerListingView.as_view(), name='worker-list'),
    path('worker-bookings/<int:worker_id>/', WorkerBookingsList.as_view(), name='worker-bookings'),
    path('submit-booking', CreateBookings.as_view(), name='submit_booking'),
    path('bookings/<int:user_id>/',ListBookings.as_view(), name='bookings'),
]