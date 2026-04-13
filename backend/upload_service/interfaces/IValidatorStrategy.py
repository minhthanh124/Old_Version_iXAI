from abc import ABC, abstractmethod
from typing import Dict, Union
from django.core.files.uploadedfile import UploadedFile

class IValidatorStrategy(ABC):
    @abstractmethod
    def validate_data(self, file: UploadedFile, data_type: str) -> Dict[str, Union[str, int]]: 
        pass
