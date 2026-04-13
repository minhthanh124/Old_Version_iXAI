from upload_app.models import ModelFile, Dataset, LabelFile, Tokenizer
from upload_app.api_root import modality_service_get_task_endpoint
import requests
from rest_framework import status
from requests.adapters import HTTPAdapter

session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount('http://modality-service:8002', adapter) # modality service
session.mount('http://upload-service:8003', adapter) # upload service
session.mount('http://gateway-service:8001', adapter) # gateway service

class UploadRepository:
    def __init__(self):
        self.type = None

    def update_meta_data(self, name, task, minio_path, data_type):
        task_field = {
            'name': task,
        }
        response = session.request(method="GET", url=modality_service_get_task_endpoint, data=task_field)
        if response.status_code == status.HTTP_200_OK:
            task_id = response.json().get("id")
        match data_type:
            case "Dataset":
                existed_data = Dataset.objects.filter(minio_path=minio_path)
                if not existed_data:
                    dataset = Dataset.objects.create(
                        name = name,
                        task = task_id,
                        minio_path = minio_path,
                    )
            case "Model":
                existed_data = ModelFile.objects.filter(minio_path=minio_path)
                if not existed_data:
                    model = ModelFile.objects.create(
                        name = name,
                        task = task_id,
                        minio_path = minio_path,
                    )
            case "Label":
                existed_data = LabelFile.objects.filter(minio_path=minio_path)
                if not existed_data:
                    label = LabelFile.objects.create(
                        name = name,
                        task = task_id,
                        minio_path = minio_path,
                    )
            case "Tokenizer":
                existed_data = Tokenizer.objects.filter(minio_path=minio_path)
                if not existed_data:
                    tokenizer = Tokenizer.objects.create(
                        name = name,
                        task = task_id,
                        minio_path = minio_path,
                    )