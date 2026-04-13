from explanation_app.models import Explanation
import requests
from rest_framework import status
from requests.adapters import HTTPAdapter

session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount('http://modality-service:8002', adapter) # modality service
session.mount('http://upload-service:8003', adapter) # upload service
session.mount('http://gateway-service:8001', adapter) # gateway service

class ExplanationRepository:
    def __init__(self):
        self.type = None

    def update_meta_data(self, method, task, dataset_path, model_path, minio_path):
        modality_response = session.request(method="GET", url=f"http://modality-service:8002/modality/get/method_task/{method}/{task}/")
        parcel = {
            "dataset_path": dataset_path,
            "model_path": model_path,
        }
        upload_response   = session.request(method="GET", url=f"http://upload-service:8003/upload/get/data_model/", params=parcel)
        if modality_response.status_code == status.HTTP_200_OK:
            task_id = modality_response.json().get("task")
            method_id = modality_response.json().get("method")
            if upload_response.status_code == status.HTTP_200_OK:
                dataset_id = upload_response.json().get("dataset")
                model_id = upload_response.json().get("model")
            existed_data = Explanation.objects.filter(model=model_id, task=task_id, method=method_id, data=dataset_id)
            if not existed_data.exists():
                explanation = Explanation.objects.create(
                    model = model_id,
                    data = dataset_id,
                    task = task_id,
                    method = method_id,
                    minio_path = minio_path,
            )