from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# authentication
from django.contrib.auth.mixins import PermissionRequiredMixin
from rest_framework.permissions import IsAuthenticated

from backend.shared.helpers.pagination_helper import get_pagination_parameters_rest
from backend.shared.helpers.handle_rest_exception_helper import (
    handle_rest_exception_helper,
)


class GeneralAPIViewService(APIView, PermissionRequiredMixin):
    # authentication class-based views - isAuth (no django permissions)
    permission_classes = [IsAuthenticated]

    # constructor
    def __init__(self, service):
        self.service = service

    # main methods =================
    def get(self, request):
        filter_params, page_number, page_size = get_pagination_parameters_rest(request)
        serialized_instances = self.service.find_all(
            filter_params, page_number, page_size
        )
        return Response(serialized_instances, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            serialized_instance = self.service.create(request.data)
            return Response(serialized_instance, status=status.HTTP_201_CREATED)
        except Exception as e:
            return self.handle_exception(e)

    def handle_exception(self, exc):
        return handle_rest_exception_helper(exc)


class GeneralDetailAPIViewService(APIView, PermissionRequiredMixin):
    # authentication class-based views - isAuth (no django permissions)
    permission_classes = [IsAuthenticated]

    # constructor
    def __init__(self, service):
        self.service = service

    # main methods =================
    def get(self, request, pk):
        try:
            serialized_instance = self.service.find_one(pk)
            return Response(serialized_instance, status=status.HTTP_200_OK)
        except Exception as e:
            return self.handle_exception(e)

    def patch(self, request, pk):
        try:
            serialized_instance = self.service.update(pk, request.data)
            return Response(serialized_instance, status=status.HTTP_200_OK)
        except Exception as e:
            return self.handle_exception(e)

    def delete(self, request, pk):
        try:
            self.service.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return self.handle_exception(e)

    def handle_exception(self, exc):
        return handle_rest_exception_helper(exc)
