from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    GatewayServiceView,
)

urlpatterns = [
    path('<str:service_name>/<path:endpoint>/', GatewayServiceView.as_view(), name="gateway-service"),
]