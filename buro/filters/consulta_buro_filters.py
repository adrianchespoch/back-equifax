from django.db.models import JSONField
from django_filters import rest_framework as filters

from backend.shared.filters.filters import BaseFilter
from buro.models.consulta_buro_model import ConsultaBuro


class ConsultaBuroFilter(BaseFilter):

    class Meta:
        filter_overrides = {
            JSONField: {
                'filter_class': filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
        model = ConsultaBuro
        fields = '__all__'


