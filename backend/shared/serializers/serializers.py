from rest_framework import serializers


# ### Filters ========================
class FiltersBaseSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(FiltersBaseSerializer, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


# ### Errors ========================
class NotFoundSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)


class BadRequestSerializerDoc(serializers.Serializer):
    status = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)
    # missing_fields = serializers.ListField(child=serializers.CharField(), required=False)
    invalid_fields = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    data = serializers.CharField(required=False)


class BadRequestSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)
    # missing_fields = serializers.ListField(required=False)
    invalid_fields = serializers.ListField(required=False)
    data = serializers.CharField(required=False)


# ### Swagger ========================
class OptionalFieldsModelSerializer(serializers.ModelSerializer):
    def get_fields(self, *args, **kwargs):
        fields = super(OptionalFieldsModelSerializer, self).get_fields(*args, **kwargs)
        for field in fields.values():
            field.required = False
        return fields


# ## Get all
class MetaSerializer(serializers.Serializer):
    next = serializers.CharField(required=False)
    previous = serializers.CharField(required=False)
    count = serializers.IntegerField(required=False)
    total_pages = serializers.IntegerField(required=False)


class QueryDocWrapperSerializer(serializers.Serializer):
    meta = MetaSerializer(required=False)
    data = serializers.ListField(required=False)
