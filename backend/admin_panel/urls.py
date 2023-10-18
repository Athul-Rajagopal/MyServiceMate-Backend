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
    path('block-unblock-user/<str:username>/', BlockUnblockUsers.as_view(), name='block-unblock-user')
]
