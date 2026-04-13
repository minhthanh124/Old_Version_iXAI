from django.shortcuts import render
from .models import Explanation
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import uuid
import requests
from rest_framework.views import APIView
from interfaces.ExplanationHandler import explanation_handler_instance
import json

class ExplanationController(APIView):
    def post(self, request, *args, **kwargs):
        all_keys = list(request.data.get("payload", {}).keys())
        modality = request.data.get("payload", {}).get("modality")
        task = request.data.get("payload", {}).get("task")
        method = request.data.get("payload", {}).get("method")
        data_key = all_keys[3:]
        data_package = {key: request.data.get("payload", {}).get(key) for key in data_key}
        response = explanation_handler_instance.handle_explanation(
            modality=modality,
            task=task,
            method=method,
            data_package=data_package,
        )
        return Response({
            "result": response.get("result"), "description": response.get("description"), "extra_data": response.get("extra_data")}, status=response.get("status"))



