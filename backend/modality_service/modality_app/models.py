from django.db import models
import uuid

class Modality(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    modality = models.ForeignKey(Modality, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Method(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=False)
    modality = models.ForeignKey(Modality, on_delete=models.CASCADE)

    def __str__(self):
        return self.name