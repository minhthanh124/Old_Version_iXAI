from django.urls import path
from .views import (
    ExplanationController,
)

urlpatterns = [
    path('post/explanation/', ExplanationController.as_view(), name='get-explanation'),
]
