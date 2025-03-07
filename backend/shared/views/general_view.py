from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from backend.shared.helpers.handle_rest_exception_helper import (
    handle_rest_exception_helper,
)
from backend.shared.exceptions.invalid_fields_exception import InvalidFieldsException
from backend.shared.exceptions.resource_not_found_exception import ResourceNotFoundException
from backend.shared.utils.common_utils import humanize_model_name
from rest_framework.exceptions import NotFound

# authentication
from django.contrib.auth.mixins import PermissionRequiredMixin
from rest_framework.permissions import IsAuthenticated


from backend.shared.utils.pagination import CustomPagination


class GeneralAPIView(APIView, PermissionRequiredMixin):
    # authentication class-based views - isAuth (no django permissions)
    permission_classes = [IsAuthenticated]

    model = None
    filter = None

    # ## serializers =================
    serializer = None  # model serializer - POST & PUT
    serializer2 = None  # Get All & Get By ID - response

    # ## auxiliar methods =================
    # override post method
    def custom_post_method(self, request, valid_data, raw_data, serializer):
        return None

    def find_all_extended_qs(self, queryset, filter_params=None):
        return queryset

    def find_all_post_serializer(self, queryset, paginated_serialized_data, filter_params=None):
        return paginated_serialized_data

    # ## main methods =================
    def get(self, request):
        try:
            queryset = self.model.objects.all().order_by("-created_at")
            pagination = CustomPagination()

            # filters -----------
            filter_values = self.filter(request.GET, queryset=queryset)
            queryset = filter_values.qs
            new_qs = self.find_all_extended_qs(
                queryset, filter_values)

            result_page = pagination.paginate_queryset(new_qs, request)
            serializer = self.serializer2(result_page, many=True)
            pagidated_data = pagination.get_paginated_response(serializer.data)
            pagidated_data['data'] = self.find_all_post_serializer(
                queryset, pagidated_data['data'], filter_values)

            return Response(pagidated_data, status=status.HTTP_200_OK)
        except Exception as e:
            if isinstance(e, NotFound):
                return Response({
                    'meta': {
                        'next': None,
                        'previous': None,
                        'count': 0,
                        'total_pages': 0,
                        'message': 'Página inválida'
                    },
                    'data': []
                }, status=status.HTTP_200_OK)
            return handle_rest_exception_helper(e)

    def post(self, request):
        try:
            serializer = self.serializer(data=request.data)
            if serializer.is_valid():
                aux_serializer = self.custom_post_method(
                    request=request, valid_data=serializer.validated_data, raw_data=request.data, serializer=serializer
                )
                if aux_serializer:  # total override
                    aux_serializer.save()
                    return Response({
                        'status': status.HTTP_201_CREATED,
                        'message': 'Elemento creado',
                        'data': aux_serializer.data
                    }, status=status.HTTP_201_CREATED)
                serializer.save()  # after to be override
                return Response({
                    'status': status.HTTP_201_CREATED,
                    'message': 'Elemento creado',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)

            raise InvalidFieldsException(
                message="Bad Request", fields=serializer.errors.items()
            )
        except Exception as e:
            return handle_rest_exception_helper(e)


class GeneralDetailAPIView(APIView, PermissionRequiredMixin):
    # authentication class-based views - isAuth (no django permissions)
    permission_classes = [IsAuthenticated]

    model = None

    # ## serializers =================
    serializer = None  # model serializer - POST & PUT
    serializer2 = None  # Get All & Get By ID - response

    # ## auxiliar methods =================
    def custom_patch_method(self, valid_data, raw_data, serializer, pk):
        return None

    # ## main methods =================
    def get(self, request, pk):
        try:
            model_instance = self.model.objects.filter(pk=pk).first()
            if model_instance is None:
                humanized_model_name = humanize_model_name(self.model.__name__)
                raise ResourceNotFoundException(
                    message=f"{humanized_model_name} con ID '{pk}' no encontrado"
                )
            serializer = self.serializer2(model_instance)
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'Elemento encontrado',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return handle_rest_exception_helper(e)

    def patch(self, request, pk):
        try:
            model_instance = self.model.objects.filter(pk=pk).first()
            if model_instance is None:
                humanized_model_name = humanize_model_name(self.model.__name__)
                raise ResourceNotFoundException(
                    message=f"{humanized_model_name} con ID '{pk}' no encontrado"
                )
            serializer = self.serializer(
                model_instance, data=request.data, partial=True)
            if serializer.is_valid():
                aux_serializer = self.custom_patch_method(
                    valid_data=serializer.validated_data,
                    raw_data=request.data,
                    serializer=serializer,
                    pk=pk,
                )
                if aux_serializer:  # total override
                    aux_serializer.save()
                    return Response({
                        'status': status.HTTP_200_OK,
                        'message': 'Elemento actualizado',
                        'data': aux_serializer.data
                    }, status=status.HTTP_200_OK)
                serializer.save()
                return Response({
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento actualizado',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

            raise InvalidFieldsException(
                message="Bad Request", fields=serializer.errors.items()
            )

        except Exception as e:
            return handle_rest_exception_helper(e)

    def delete(self, request, pk):
        try:
            model_instance = self.model.objects.filter(pk=pk).first()
            if model_instance is None:
                humanized_model_name = humanize_model_name(self.model.__name__)
                raise ResourceNotFoundException(
                    message=f"{humanized_model_name} con ID '{pk}' no encontrado"
                )
            model_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return handle_rest_exception_helper(e)
