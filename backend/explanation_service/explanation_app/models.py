from django.db import models
import uuid

# Create your models here.
class Explanation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.UUIDField(default=uuid.uuid4, editable=False)
    data = models.UUIDField(default=uuid.uuid4, editable=False)
    task = models.UUIDField(default=uuid.uuid4, editable=False)
    method = models.UUIDField(default=uuid.uuid4, editable=False)
    minio_path = models.CharField(max_length=255, default='')
