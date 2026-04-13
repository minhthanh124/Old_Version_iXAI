import tempfile
import os
from rest_framework import status
from explanation_service import settings
from minio import Minio
from minio.error import S3Error
from pathlib import Path
from django.core.cache import cache
from interfaces.TimeScheduler import schedule_file_deletion, schedule_folder_deletion
from typing import Any, Dict, Optional, List
from io import BytesIO
import base64
import uuid

class MinIODownloader:
    def __init__(self):
        self.minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
    
    def download_from_minio(self, path):
        bucket_name = '123456-234567'
        local_files = {}
        response = None
        key = f"{path}"
        uploads = cache.get(key)
    
        try:
            is_single_file = False
            try:
                self.minio_client.stat_object(bucket_name, path)
                is_single_file = True
            except S3Error as e:
                if e.code != 'NoSuchKey':
                    raise e
            if not is_single_file:
                if uploads is None:
                    objects = self.minio_client.list_objects(bucket_name, prefix=path, recursive=True)
                    objects_list = list(objects)
                    
                    if not objects_list:
                        return {
                            "status": "error",
                            "message": f"No files found at path: {path}"
                        }
                    path_basename = Path(path).name or "downloaded_folder"
                    temp_dir = tempfile.mkdtemp()
                    local_folder = os.path.join(temp_dir, path_basename)
                    os.makedirs(local_folder, exist_ok=True)
                    local_files[path] = local_folder
                    for obj in objects_list:
                        object_name = obj.object_name
                        suffix = Path(object_name).suffix or ".tmp"
                        relative_path = os.path.relpath(object_name, path)
                        local_file_path = os.path.join(local_folder, relative_path)
                        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                        with open(local_file_path, 'wb') as local_file:
                            response = self.minio_client.get_object(bucket_name, object_name)
                            for chunk in response.stream(4096 * 4096):
                                local_file.write(chunk)
                            local_files[object_name] = local_file_path
                        cache.set(key, local_files)
                        schedule_folder_deletion(temp_dir, key, delay_seconds=3600)
                else:
                    local_files = uploads
            else:
                object_name = f"{path}"
                if uploads is None:
                    response = self.minio_client.get_object(bucket_name, object_name)
                    suffix = Path(path).suffix or ".tmp"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        for chunk in response.stream(4096 * 4096):
                            tmp_file.write(chunk)
                        local_files[object_name] = tmp_file.name
                    cache.set(key, local_files)
                    schedule_file_deletion(tmp_file.name, key, delay_seconds=1000)
                else:
                    local_files = uploads
            
            if not local_files:
                return {"status": "failure", "message": "No files downloaded"}
            return {"status": "success", "local_path": local_files}

        except S3Error as e:
            return {"status": "failure", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
        finally:
            if response is not None:
                try:
                    response.close()
                    response.release_conn()
                except:
                    pass

    def upload_to_minio(self, data, task, method):
        bucket_name = '123456-234567'
        file_path = f"{bucket_name}/ExplanationResults/{task}/{method}/"
        transformed_data = None
        if "image_base64" in data and data["image_base64"]:
            transformed_data = base64.b64decode(data["image_base64"])
            file_path = file_path + f"output_{uuid.uuid4()}.png"
        elif "html_str" in data and data["html_str"]:
            transformed_data = data["html_str"].encode("utf-8")
            file_path = file_path + f"output_{uuid.uuid4()}.html"
        if "plot_waterfall" in data and data["plot_waterfall"]:
            transformed_data = base64.b64decode(data["plot_waterfall"])
            file_path = file_path + f"output_{uuid.uuid4()}.png"
        self.minio_client.put_object(
            bucket_name,
            file_path,
            BytesIO(transformed_data),
            length=len(transformed_data),
            content_type="application/octet-stream"
        )
        return file_path        
