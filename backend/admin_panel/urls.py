from django.urls import path, include
from .views import *

urlpatterns = [
    path('worker-approval-requests/', WorkerApprovalRequestListView.as_view(), name='worker-approval-requests'),
    path('worker-approval/<int:worker_id>/', WorkerApprovalView.as_view(), name='worker-approval'),
]
