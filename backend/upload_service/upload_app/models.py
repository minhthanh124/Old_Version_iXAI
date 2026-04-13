from django.db import models
import uuid

class ModelFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    task = models.UUIDField(default=uuid.uuid4, editable=False)
    minio_path = models.CharField(max_length=255, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.version})"

class Dataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    task = models.UUIDField(default=uuid.uuid4, editable=False)
    minio_path = models.CharField(max_length=255, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class LabelFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    task = models.UUIDField(default=uuid.uuid4, editable=False)
    minio_path = models.CharField(max_length=255, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Tokenizer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    task = models.UUIDField(default=uuid.uuid4, editable=False)
    minio_path = models.CharField(max_length=255, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name