import django_filters
from django.db.models import ForeignKey, CharField, DateField, DateTimeField


# class BaseFilter(django_filters.FilterSet):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         model_fields = self.Meta.model._meta.fields # type: ignore

#         for field in model_fields:
#             if hasattr(field, "name"):
#                 field_name = field.name
#                 # if isinstance(field, ForeignKey):
#                 #     related_field_name = f"{field_name}__codigo"
#                 #     self.filters[field_name] = django_filters.CharFilter(
#                 #         field_name=related_field_name, lookup_expr="icontains"
#                 #     )
#                 #     continue
#                 if isinstance(field, CharField):
#                     self.filters[field_name] = django_filters.CharFilter(
#                         field_name=field_name, lookup_expr="icontains"
#                     )
#                 if isinstance(field, DateField) or isinstance(field, DateTimeField):
#                     self.filters[field_name] = django_filters.DateRangeFilter(
#                         field_name=field_name
#                     )
#                     self.filters[field_name] = django_filters.DateFilter(
#                         field_name=field_name, lookup_expr="icontains"
#                     )


class BaseFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        model_fields = self.Meta.model._meta.fields
        for field in model_fields:
            if hasattr(field, "name"):
                field_name = field.name
                self.filters[field_name] = django_filters.CharFilter(
                    field_name=field_name, lookup_expr="icontains"
                )
                if isinstance(field, DateField) or isinstance(field, DateTimeField):
                    self.filters[field_name] = django_filters.DateRangeFilter(
                        field_name=field_name
                    )
                    self.filters[field_name] = django_filters.DateFilter(
                        field_name=field_name, lookup_expr="icontains"
                    )
