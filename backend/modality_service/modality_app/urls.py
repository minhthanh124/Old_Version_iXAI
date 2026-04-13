from django.urls import path
from .views import (
    ModalityController,
    TaskController,
    XAIMethodController,
    GetModalityPerNameView,
    GetTaskPerNameView,
)

urlpatterns = [
    path('get_modality/', ModalityController.as_view(), name='get_modality'),
    path('get_task/', TaskController.as_view(), name='get_task'),
    path('get/method_task/<str:method_name>/<str:task_name>/', XAIMethodController.as_view(), name='get_method'),
    path('get_task_per_name/', GetTaskPerNameView.as_view(), name='get-task-pername'),

]
