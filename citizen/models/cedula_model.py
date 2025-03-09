import uuid
from django.db import models

from backend.shared.models.models import AuditDateModel
from backend.shared.constants.choices import TIPO_IDENTIFICACION_REGISTRO_CIVIL_CHOICES


class Cedula(AuditDateModel):
    id_cedula = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    identificacion = models.CharField(max_length=20)
    tipo_identificacion = models.CharField(
        max_length=75, choices=TIPO_IDENTIFICACION_REGISTRO_CIVIL_CHOICES)

    fullName = models.CharField(max_length=255)
    nacionalidad = models.CharField(max_length=50)
    condicionCedulado = models.CharField(max_length=100)
    esDiscapacitado = models.BooleanField(default=False)
    fechaNacimiento = models.CharField(max_length=10)  # formato "dd/MM/yyyy"
    edad = models.IntegerField(default=0)
    esTerceraEdad = models.BooleanField(default=False)

    # Campos opcionales
    nombreMadre = models.CharField(max_length=255, null=True, blank=True)
    nombrePadre = models.CharField(max_length=255, null=True, blank=True)
    numeroCasa = models.CharField(max_length=50, null=True, blank=True)
    profesion = models.CharField(max_length=100, null=True, blank=True)
    sexo = models.CharField(max_length=20, null=True, blank=True)
    calle = models.CharField(max_length=255, null=True, blank=True)
    lugarNacimiento = models.CharField(max_length=255, null=True, blank=True)
    codigoError = models.CharField(max_length=20, null=True, blank=True)
    conyuge = models.CharField(max_length=255, null=True, blank=True)
    domicilio = models.CharField(max_length=255, null=True, blank=True)
    error = models.CharField(max_length=255, null=True, blank=True)
    estadoCivil = models.CharField(max_length=50, null=True, blank=True)
    genero = models.CharField(max_length=20, null=True, blank=True)
    instruccion = models.CharField(max_length=100, null=True, blank=True)
    lugarInscripcionGenero = models.CharField(
        max_length=255, null=True, blank=True)
    fechaCedulacion = models.CharField(max_length=10, null=True, blank=True)
    fechaInscripcionDefuncion = models.CharField(
        max_length=10, null=True, blank=True)
    fechaInscripcionGenero = models.CharField(
        max_length=10, null=True, blank=True)

    # Fecha límite para refetch
    fechaLimitRefetch = models.DateTimeField()
