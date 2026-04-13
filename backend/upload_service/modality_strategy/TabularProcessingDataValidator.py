from interfaces.IValidatorStrategy import IValidatorStrategy
import os
from rest_framework import status

class TabularProcessingDataValidator(IValidatorStrategy):
    def __init__(self):
        self.dataset_rules = ['.xlsx', '.csv']
        self.model_rules   = ['.pth', '.pkl']
        self.label_rules   = ['.txt', '.json']

    def get_file_extension(self, file_name):
        return os.path.splitext(file_name)[1]

    def validate_data(self, file, data_type):
        if not isinstance(data_type, str) or not isinstance(file.name, str):
            return {"message": "Invalid format", "status": status.HTTP_400_BAD_REQUEST}
        match data_type:
            case "Dataset":
                if self.get_file_extension(file.name) in self.dataset_rules:
                    return {"message": "Valid", "status": status.HTTP_200_OK}                    
            case "Model":
                if self.get_file_extension(file.name) in self.model_rules:
                    return {"message": "Valid", "status": status.HTTP_200_OK} 
            case "Label":
                if self.get_file_extension(file.name) in self.label_rules:
                    return {"message": "Valid", "status": status.HTTP_200_OK}
            case "Tokenizer":
                if get_file_extension(file.name) in self.tokenizer_rules:
                    return {"message": "Valid", "status": status.HTTP_200_OK}
        return {"message": "The file is unsupported.", "status": status.HTTP_400_BAD_REQUEST}