from rest_framework import serializers

from backend.shared.serializers.serializers import (
    FiltersBaseSerializer,
    QueryDocWrapperSerializer,
)
from buro.models.consulta_buro_model import ConsultaBuro


# ### ConsultaBuro Serializer - Model ===============
class ConsultaBuroSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultaBuro
        fields = '__all__'


class ConsultaEQUIFAXSerializer(serializers.ModelSerializer):
    identificacion = serializers.CharField()

    class Meta:
        model = ConsultaBuro
        fields = [
            'identificacion', 'tipo_identificacion', 'schema_name', 'usuario_uuid', 'empresa_uuid'
        ]

    def validate(self, data):
        identificacion = data.get('identificacion')
        if len(identificacion) < 10:
            raise serializers.ValidationError(
                'Identificación debe tener al menos 10 caracteres')
        return data


class ConsultarEquifaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultaBuro
        fields = '__all__'


# ## Response: Get All & Get By ID ===============
class ConsultaBuroResponseSerializer(FiltersBaseSerializer):
    class Meta:
        model = ConsultaBuro
        fields = '__all__'


# ### Filter Serializer - Get All ===============
class ConsultaBuroFilterSerializer(FiltersBaseSerializer):
    class Meta:
        model = ConsultaBuro
        fields = '__all__'


# ### Swagger ===============
# ## Response Body: Post & Put & Patch
class ConsultaBuroOptDocSerializer(FiltersBaseSerializer):
    class Meta:
        model = ConsultaBuro
        fields = '__all__'


# ## Get All Response
class ConsultaBuroQueryDocWrapperSerializer(QueryDocWrapperSerializer):
    data = ConsultaBuroResponseSerializer(many=True, required=False)
