from rest_framework import serializers

from backend.shared.serializers.serializers import (
    FiltersBaseSerializer,
    QueryDocWrapperSerializer,
)
from citizen.models.cedula_model import Cedula


# ### Cedula Serializer - Model ===============
class CedulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cedula
        fields = '__all__'


class ConsultaCedulaSerializer(serializers.ModelSerializer):
    cedula = serializers.CharField(min_length=10, max_length=12)
    class Meta:
        model = Cedula
        fields = ['cedula']


# ## Response: Get All & Get By ID
class CedulaResponseSerializer(FiltersBaseSerializer):
    class Meta:
        model = Cedula
        fields = '__all__'


# ### Filter Serializer - Get All ===============
class CedulaFilterSerializer(FiltersBaseSerializer):
    class Meta:
        model = Cedula
        fields = '__all__'


# ### Swagger ===============
# ## Response Body: Post & Put & Patch
class CedulaOptDocSerializer(FiltersBaseSerializer):
    class Meta:
        model = Cedula
        fields = '__all__'


# ## Get All Response
class CedulaQueryDocWrapperSerializer(QueryDocWrapperSerializer):
    data = CedulaResponseSerializer(many=True, required=False)
