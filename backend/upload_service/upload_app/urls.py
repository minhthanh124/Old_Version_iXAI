from django.urls import path
from .views import (
    UploadDataController,
)

urlpatterns = [
    path('post/data/', UploadDataController.as_view(), name='post-data'),
    path('get/data_model/', UploadDataController.as_view(), name='get-data'),
]
