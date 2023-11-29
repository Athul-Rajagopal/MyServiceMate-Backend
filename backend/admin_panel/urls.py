from django.urls import path, include
from .views import *

urlpatterns = [
    path('worker-approval-requests/', WorkerApprovalRequestListView.as_view(), name='worker-approval-requests'),
    path('worker-approval/<int:worker_id>/', WorkerApprovalView.as_view(), name='worker-approval'),
    path('create-service/',ServiceCreateView.as_view(), name='create_service'),
    path('delete-service/<int:pk>/', ServiceDeleteView.as_view(), name='service-delete'),
    path('create-location/', LocationCreateView.as_view(), name='create_location'),
    path('remove-location/<int:pk>/', RemoveLocationView.as_view(), name='remove-location'),
    path('workers/', GetWorkersList.as_view(), name='workers'),
    path('users/',GetuserList.as_view(), name='users'),
    path('block-unblock-user/<str:username>/', BlockUnblockUsers.as_view(), name='block-unblock-user'),
    path('worker-bookings/<int:worker_id>/',WorkerBookingsList.as_view(), name='worker-bookings'),
    path('user-bookings/<str:user_name>/',UserBookingsList.as_view(), name='user-bookings'),
    path('booking-statistics/',booking_statistics,name='booking-statistics'),
    path('service-statistics/', service_statistics, name='service-statistics'),
    path('worker-approval-requests-count/',PendingApprovalRequestCount.as_view(),name='worker-approval-requests-count'),
    path('transactions/',Transactions.as_view(),name='transactions'),
    path('admin-wallet/',AdminWalletView.as_view(),name='admin-wallet'),
    path('edit-service/<int:service_id>/',ServiceEditView.as_view(),name='edit-service'),
    path('edit-location/<int:location_id>',EditLocation.as_view(),name='edit-location'),
]
