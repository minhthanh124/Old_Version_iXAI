import requests
from django.shortcuts import render

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .api_root import *
from requests.adapters import HTTPAdapter
from requests.exceptions import JSONDecodeError

session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10)
session.mount('http://modality-service:8002', adapter) # modality service
session.mount('http://upload-service:8003', adapter) # upload service
session.mount('http://explanation-service:8005', adapter) # explanation service
session.mount('http://gateway-service:8001', adapter) # gateway service

# Create your views here.
class GatewayServiceView(APIView):    
    SERVICE_MAP = {
        "modality": modality_service_path,
        "upload": upload_service_path,
        "explanation": explanation_service_path,
    }

    def forward_request(self, service_name, request, method, endpoint, data=None, params=None):

        try:
            target_url = f"{self.SERVICE_MAP[service_name]}{endpoint}"
            if not target_url.endswith('/'):
                target_url += '/'

            if request.FILES:
                files = []
                for field, file_list in request.FILES.lists():
                    for file in file_list:
                        files.append((field, (file.name, file, file.content_type)))

                data = request.POST.dict()
                response = session.request(method=method.upper(), url=target_url, files=files, data=data)
            else:
                response = session.request(
                    method=method.upper(),
                    url=target_url,
                    json=data if data else None,
                    params=params
                )
            try:
                data = response.json()
            except ValueError:
                data = {"raw_response": response.text} if response.text else {}
            return Response(data, status=response.status_code)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": "Service unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def get(self, request, service_name, endpoint):
        response = self.forward_request(service_name, request, "GET", endpoint, params=request.query_params)
        return response

    def post(self, request, service_name, endpoint):
        return self.forward_request(service_name, request, "POST", endpoint, data=request.data)

    def put(self, request, service_name, endpoint):
        return self.forward_request(service_name, request, "PUT", endpoint, data=request.data)

    def delete(self, request, service_name, endpoint):
        return self.forward_request(service_name, request, "DELETE", endpoint, data=request.data)