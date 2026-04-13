from upload_app.models import ModelFile, Dataset, LabelFile, Tokenizer
from upload_app.api_root import modality_service_get_task_endpoint
import requests
from rest_framework.response import Response
from rest_framework import status
import uuid
from storage.MinIOUploader import MinIOUploader
from storage.UploadRepository import UploadRepository
import importlib

class UploadHandler:
    def __init__(self):
        self.module_path = "modality_strategy."
        self.session_id = "123456-234567"
        self.minio_uploader = MinIOUploader()
        self.upload_repository = UploadRepository()

    def handle_upload(self, modality, task, data_type, files):
        folder_name = ""
        file_path = ""
        if not isinstance(files, list):
            files = [files]
        validator = self.get_modality_data_validator(modality)
        if data_type == "Tokenizer":
            folder_name = str(uuid.uuid4().hex)
        for file in files:
            response = validator.validate_data(file, data_type)
            if response.get("status") == status.HTTP_200_OK:
                result = self.minio_uploader.upload_to_minio(self.session_id, task, data_type, file, folder_name)
                if result.get("status") == "success":
                    file_path = result.get("file_path")
                    self.upload_repository.update_meta_data(file.name, task, file_path, data_type)
            else:
                return {"message": response.get("message"), "status": response.get("status")}
        return {"message": file_path, "status": status.HTTP_200_OK}

    def get_modality_data_validator(self, modality):
        modality_path = modality.replace(" ","") + "DataValidator"
        module_path = self.module_path + modality_path
        module = importlib.import_module(module_path)
        uploader_class = getattr(module, modality_path)
        uploader = uploader_class()
        return uploader

upload_handler_instance = UploadHandler()