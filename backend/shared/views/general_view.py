from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import status
from django.http import JsonResponse

# authentication
from django.contrib.auth.mixins import PermissionRequiredMixin
from rest_framework.permissions import IsAuthenticated


from backend.shared.utils.pagination import CustomPagination
from backend.dtos import ErrorResponseDTO, NotFoundErrorResponseDTO


class GeneralAPIView(APIView, PermissionRequiredMixin):
    # authentication class-based views - isAuth (no django permissions)
    permission_classes = [IsAuthenticated]

    model = None
    filter = None
    required_fields = []

    # ## serializers =================
    serializer = None  # model serializer - POST & PUT
    serializer2 = None  # Get All & Get By ID - response

    # ## auxiliar methods =================
    # override post method
    def custom_post_method(self, request, serialized):
        return None

    # ## main methods =================
    def get(self, request):
        queryset = self.model.objects.all().order_by("created_at")
        pagination = CustomPagination()

        # filters
        filter_values = self.filter(request.GET, queryset=queryset)
        queryset = filter_values.qs

        result_page = pagination.paginate_queryset(queryset, request)
        serializer = self.serializer2(result_page, many=True)
        return pagination.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            aux_post_method_res = self.custom_post_method(
                request=request, serialized=serializer
            )
            if aux_post_method_res:  # total override
                return aux_post_method_res
            # model_instance = serializer.save() # after to override
            serializer.save()  # after to be override
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Transform the errors dictionary into a list of strings
        invalid_fields = [
            f"{field}: {error}"
            for field, errors in serializer.errors.items()
            for error in errors
        ]
        bad_request = ErrorResponseDTO(
            status=status.HTTP_400_BAD_REQUEST,
            message="Bad Request",
            invalid_fields=invalid_fields,
        )
        return Response(bad_request.__dict__, status=status.HTTP_400_BAD_REQUEST)


class GeneralDetailAPIView(APIView, PermissionRequiredMixin):
    # authentication class-based views - isAuth (no django permissions)
    permission_classes = [IsAuthenticated]

    model = None
    required_fields = []  # additonal fields to validate

    # ## serializers =================
    serializer = None  # model serializer - POST & PUT
    serializer2 = None  # Get All & Get By ID - response

    # ## auxiliar methods =================
    def custom_patch_method(self, request, serialized):
        return None

    # ## main methods =================
    def get(self, request, pk):
        try:
            model_instance = get_object_or_404(self.model, pk=pk)
            serializer = self.serializer2(model_instance)
            return Response(serializer.data)
        except Http404:
            not_found = NotFoundErrorResponseDTO(
                status=status.HTTP_404_NOT_FOUND,
                message=f"{self.model.__name__} with id '{pk}' not found",
            )
            return JsonResponse(not_found.__dict__, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        try:
            model_instance = get_object_or_404(self.model, pk=pk)
            serializer = self.serializer(
                model_instance, data=request.data, partial=True
            )
            if serializer.is_valid():
                aux_patch_method_res = self.custom_patch_method(
                    request=request, serialized=serializer
                )
                if aux_patch_method_res:  # total override
                    return aux_patch_method_res
                serializer.save()  # after to be override
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Transform the errors dictionary into a list of strings
            invalid_fields = [
                f"{field}: {error}"
                for field, errors in serializer.errors.items()
                for error in errors
            ]
            bad_request = ErrorResponseDTO(
                status=status.HTTP_400_BAD_REQUEST,
                message="Bad Request",
                invalid_fields=invalid_fields,
            )
            return Response(bad_request.__dict__, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            not_found = NotFoundErrorResponseDTO(
                status=status.HTTP_404_NOT_FOUND,
                message=f"{self.model.__name__} with id '{pk}' not found",
            )
            return JsonResponse(not_found.__dict__, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            error = ErrorResponseDTO(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e)
            )
            return Response(
                error.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        try:
            model_instance = get_object_or_404(self.model, pk=pk)
            model_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            not_found = NotFoundErrorResponseDTO(
                status=status.HTTP_404_NOT_FOUND,
                message=f"{self.model.__name__} with id '{pk}' not found",
            )
            return JsonResponse(not_found.__dict__, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            error = ErrorResponseDTO(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e)
            )
            return Response(
                error.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
