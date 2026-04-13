
import requests
import importlib
from rest_framework import status
import pandas as pd

def validate_label_file(label_path):
    df = pd.read_excel(label_path)
    required_columns = {"Index", "Name"}
    if not required_columns.issubset(df.columns):
        return {"message": f"The label file is missing required columns: {required_columns - set(df.columns)}", "status": status.HTTP_400_BAD_REQUEST}
    return {"message": "Label is valid", "status": status.HTTP_200_OK}
 