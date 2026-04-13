import tempfile
import os
import requests
from explanation_app.models import Explanation
from rest_framework.response import Response
from rest_framework import status
from explanation_service import settings
from minio import Minio
from minio.error import S3Error
from pathlib import Path
from django.core.cache import cache
from .TimeScheduler import schedule_file_deletion, schedule_folder_deletion
from typing import Any, Dict, Optional, List
from storage.MinIODownloader import MinIODownloader
from storage.ExplanationRepository import ExplanationRepository
import importlib

minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)

class ExplanationHandler:
    def __init__(self):
        self.module_path = "TaskExplainers."
        self.minio_downloader  = MinIODownloader()
        self.explanation_repository = ExplanationRepository()

    def handle_explanation(self, modality, task, method, data_package):
        data_path = []
        coordinator = self.get_modality_explanation_coordinator(modality)
        for key, value in data_package.items():
            if key not in ["layer", "object"]:
                result = self.minio_downloader.download_from_minio(value)
                if result["status"] == "success":
                    data_path.append((key, result['local_path']))
            else:
                data_path.append((key, value))
        result = coordinator.run_task_explainer(task, method, data_path)
        if result.get("status") == status.HTTP_200_OK:
            file_path = self.minio_downloader.upload_to_minio(result.get("result"), task, method)
            self.explanation_repository.update_meta_data(method, task, data_package["dataset_path"], data_package["model_path"], file_path)
        return result

    def get_modality_explanation_coordinator(self, modality):
        modality_path = modality.replace(" ","")
        class_path = modality_path + "ExplanationCoordinator"
        module_path = self.module_path + modality_path + "." +class_path
        module = importlib.import_module(module_path)
        generic_explainer_class = getattr(module, class_path)
        generic_explainer = generic_explainer_class()
        return generic_explainer

explanation_handler_instance = ExplanationHandler()
