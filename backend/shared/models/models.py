from django.db import models


class AuditDateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    state = models.BooleanField(default=True)

    class Meta:
        abstract = True  # to avoid creating a table for this model
