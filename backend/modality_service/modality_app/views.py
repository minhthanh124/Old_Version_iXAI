from django.shortcuts import render
from .models import Modality, Task, Method
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializer import ModalitySerializer, TaskSerializer, MethodSerializer
import uuid
import requests
from rest_framework.views import APIView

class ModalityController(APIView):
    @swagger_auto_schema(
        operation_summary="Get modality list",
        responses={
            200: ModalitySerializer(many=True),
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def get(self, request):
        modality_list = Modality.objects.all()
        if not modality_list.exists():
            return Response({'error': 'There are some problems with the system. Please try again!'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ModalitySerializer(modality_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TaskController(APIView):
    @swagger_auto_schema(
        operation_summary="Get task list for a modality",
        responses={
            200: ModalitySerializer(many=True),
            400: 'Bad Request',
            404: 'Not Found'
        }
    )
    def get(self, request):
        task_list = Task.objects.all()
        if not task_list.exists():
            return Response({'error': 'There are some problems with the system. Please try again!'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class XAIMethodController(APIView):
    def get(self, request, method_name, task_name):
        method = Method.objects.filter(name=method_name)
        task   = Task.objects.filter(name=task_name)
        if not method.exists() and not task.exists():
            return Response({'error': 'There are some problems with the system. Please try again!'}, status=status.HTTP_404_NOT_FOUND)
        return Response({"method": method.first().id, "task": task.first().id}, status=status.HTTP_200_OK)

class GetModalityPerNameView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="Modality name", type=openapi.TYPE_STRING),
        ],
         responses={
            200: ModalitySerializer(many=True),
            400: 'Bad Request',
            404: 'Not Found'
        },
    )
    def get(self, request):
        name = request.data.get('name')
        modality = Modality.objects.filter(name=name).first()
        if not modality:
            return Response({'error': 'The modality is not found!'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ModalitySerializer(modality)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetTaskPerNameView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="Task name", type=openapi.TYPE_STRING),
        ],
         responses={
            200: TaskSerializer(many=True),
            400: 'Bad Request',
            404: 'Not Found'
        },
    )
    def get(self, request):
        name = request.data.get('name')
        task = Task.objects.filter(name=name).first()
        if not task:
            return Response({'error': 'The modality is not found!'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)