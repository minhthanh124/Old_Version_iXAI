import threading
import shutil
import os
from django.core.cache import cache

def schedule_file_deletion(file_path, key, delay_seconds=3600):
    def delete_file():
        if os.path.exists(file_path):
            os.remove(file_path)
            cache.delete(key)
    timer = threading.Timer(delay_seconds, delete_file)
    timer.start()

def schedule_folder_deletion(folder_path, key, delay_seconds=3600):
    def delete_folder():
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            cache.delete(key)
    timer = threading.Timer(delay_seconds, delete_folder)
    timer.start()