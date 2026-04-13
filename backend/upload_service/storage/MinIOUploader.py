from minio import Minio
from minio.error import S3Error
from upload_service import settings

class MinIOUploader:
    def __init__(self):
        self.minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    def ensure_bucket(self, bucket_name):
        if not self.minio_client.bucket_exists(bucket_name):
            self.minio_client.make_bucket(bucket_name)

    def upload_to_minio(self, session_id, task, data_type, file, folder_name=""):
        bucket_name = str(session_id)
        self.ensure_bucket(bucket_name)
        file_path = f"{bucket_name}/{data_type}/{task}/"
        if data_type == "Tokenizer":
            file_path = file_path + f"{folder_name}/{file.name}"
        else:
            file_path = file_path + f"{file.name}"
        try:
            file.seek(0)
            self.minio_client.put_object(bucket_name, file_path, file, length=file.size, content_type='application/octet-stream')
        except S3Error as e:
            return {"status": "error"}
        if data_type == "Tokenizer":
            return {"status": "success", "file_path": f"{bucket_name}/{data_type}/{task}/{folder_name}"}
        return {"status": "success", "file_path": file_path}

    def remove_bucket(self, bucket_name):
        self.minio_client.remove_bucket(bucket_name)