import uuid
from django.db import models

from backend.shared.models.models import AuditDateModel
from backend.shared.constants.choices import TIPO_IDENTIFICACION_EQUIFAX_CHOICES


class ConsultaBuro(AuditDateModel):
    id_consulta_buro = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    identificacion = models.CharField(max_length=20)
    tipo_identificacion = models.CharField(
        max_length=75, choices=TIPO_IDENTIFICACION_EQUIFAX_CHOICES)

    response_data = models.JSONField(
        null=True, blank=True, default=dict)
    raw_data = models.JSONField(
        null=True, blank=True, default=dict)

    schema_name = models.CharField(max_length=200)
    usuario_uuid = models.UUIDField()
    empresa_uuid = models.UUIDField()

    valid_until = models.DateTimeField(null=True, blank=True)
