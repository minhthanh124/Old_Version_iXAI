from django.shortcuts import render
from .models import ModelFile, Dataset, LabelFile, Tokenizer
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
import uuid
import requests
from rest_framework.views import APIView
from interfaces.UploadHandler import upload_handler_instance

class UploadDataController(APIView):
    def post(self, request):
        task = request.data.get("task")
        modality = request.data.get("modality")
        data_type = request.data.get("data_type")
        dataset_files = request.FILES.getlist("files")
        if not dataset_files or not modality or not task:
            return Response({'error': 'No dataset provided!'}, status=status.HTTP_404_NOT_FOUND)
        response = upload_handler_instance.handle_upload(
            modality=modality,
            task=task,
            data_type=data_type,
            files=dataset_files
        )
        return Response({
            "message": response.get("message")}, status=response.get("status"))
    
    def get(self, request):
        dataset_path = request.query_params.get("dataset_path")
        model_path = request.query_params.get("model_path")
        dataset = Dataset.objects.filter(minio_path=dataset_path)
        model = ModelFile.objects.filter(minio_path=model_path)
        if not dataset.exists() and not model.exists():
            return Response({'error': 'There are some problems with the system. Please try again!'}, status=status.HTTP_404_NOT_FOUND)
        return Response({"dataset": dataset.first().id, "model": model.first().id}, status=status.HTTP_200_OK)
