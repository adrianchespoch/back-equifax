from backend.shared.filters.filters import BaseFilter
from citizen.models.cedula_model import Cedula


class CedulaFilter(BaseFilter):
    class Meta:
        model = Cedula
        fields = '__all__'
