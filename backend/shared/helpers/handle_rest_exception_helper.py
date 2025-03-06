from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.exceptions import NotAuthenticated
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken

import traceback


from backend.dtos import (
    ErrorResponseDTO,
    NotFoundErrorResponseDTO,
    UnauthorizedErrorResponseDTO,
)
from backend.shared.exceptions.resource_not_found_exception import (
    ResourceNotFoundException,
)
from backend.shared.exceptions.invalid_fields_exception import InvalidFieldsException
from backend.shared.exceptions.unauthorized_exception import UnauthorizedException


def handle_rest_exception_helper(exc):

    if isinstance(exc, InvalidToken):
        error = UnauthorizedErrorResponseDTO(
            status=status.HTTP_401_UNAUTHORIZED, message="Invalid token"
        )
        return Response(error.__dict__, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, NotAuthenticated) or isinstance(exc, UnauthorizedException):
        error = UnauthorizedErrorResponseDTO(
            status=status.HTTP_401_UNAUTHORIZED, message=str(exc)
        )
        return Response(error.__dict__, status=status.HTTP_401_UNAUTHORIZED)

    if isinstance(exc, ResourceNotFoundException):
        not_found = NotFoundErrorResponseDTO(
            status=status.HTTP_404_NOT_FOUND,
            message=str(exc),
        )
        return JsonResponse(not_found.__dict__, status=status.HTTP_404_NOT_FOUND)
    elif isinstance(exc, InvalidFieldsException):
        invalid_fields = [
            f"{field}: {error}" for field, errors in exc.fields for error in errors
        ]
        bad_request = ErrorResponseDTO(
            status=status.HTTP_400_BAD_REQUEST,
            message=str(exc),
            invalid_fields=invalid_fields,
        )
        return Response(bad_request.__dict__, status=status.HTTP_400_BAD_REQUEST)
    else:
        print(traceback.format_exc())
        error = ErrorResponseDTO(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(exc),
        )
        return Response(error.__dict__, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
