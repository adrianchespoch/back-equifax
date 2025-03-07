from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

# ## docs openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from backend.shared.views.general_view import GeneralAPIView, GeneralDetailAPIView
from backend.shared.constants.constants import page_size_openapi, page_openapi
from backend.shared.serializers.serializers import (
    BadRequestSerializerDoc,
    NotFoundSerializer,
)

from buro.filters.consulta_buro_filters import ConsultaBuroFilter
from buro.models.consulta_buro_model import ConsultaBuro
from buro.serializers.consulta_buro_serializers import (
    ConsultaBuroSerializer,
    ConsultaBuroQueryDocWrapperSerializer,
    ConsultaBuroResponseSerializer,
    ConsultaBuroFilterSerializer,
    ConsultaBuroOptDocSerializer,
)

from buro.helpers.sanitize_equifax_data_helper import SanitizeEquifaxDataHelper
from buro.helpers.equifax_api_helper import EquifaxAPIHelper
from backend.settings import (
    EQUIFAX_SERVICE_API_URL,
    STAGE,
)
from backend.shared.exceptions.custom_generic_exception import CustomGenericException
from backend.shared.helpers.handle_rest_exception_helper import handle_rest_exception_helper


class ConsultaBuroView(GeneralAPIView):
    model = ConsultaBuro
    filter = ConsultaBuroFilter

    serializer = ConsultaBuroSerializer  # model serializer
    serializer2 = ConsultaBuroResponseSerializer  # response

    @swagger_auto_schema(
        operation_description="Get All ConsultaBuros",
        responses={
            200: openapi.Response("OK", ConsultaBuroQueryDocWrapperSerializer),
        },
        query_serializer=ConsultaBuroFilterSerializer,
        manual_parameters=[page_size_openapi, page_openapi],
    )
    def get(self, request):
        return super().get(request)

    @swagger_auto_schema(
        operation_description="Create ConsultaBuro",
        request_body=ConsultaBuroSerializer,
        responses={
            201: openapi.Response("OK", ConsultaBuroOptDocSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializerDoc),
        },
    )
    def post(self, request):
        return super().post(request)


class ConsultaBuroDetailView(GeneralDetailAPIView):
    model = ConsultaBuro

    serializer = ConsultaBuroSerializer
    serializer2 = ConsultaBuroResponseSerializer

    @swagger_auto_schema(
        operation_description="Get ConsultaBuro by ID",
        responses={
            200: openapi.Response("OK", ConsultaBuroResponseSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
        },
    )
    def get(self, request, pk):
        return super().get(request, pk)

    @swagger_auto_schema(
        operation_description="Update ConsultaBuro",
        request_body=ConsultaBuroSerializer,
        responses={
            200: openapi.Response("OK", ConsultaBuroOptDocSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializerDoc),
        },
    )
    def patch(self, request, pk):
        return super().patch(request, pk)

    @swagger_auto_schema(
        operation_description="Delete ConsultaBuro",
        responses={
            204: openapi.Response("Ok - No Content"),
            404: openapi.Response("Not Found", NotFoundSerializer),
        },
    )
    def delete(self, request, pk):
        return super().delete(request, pk)


# =====================================
@swagger_auto_schema(
    method='post',
    operation_description="Create ConsultaBuro",
    request_body=ConsultaBuroSerializer,
    responses={
        201: openapi.Response("OK", ConsultaBuroOptDocSerializer),
        400: openapi.Response("Bad Request", BadRequestSerializerDoc),
    },
)
@api_view(["POST"])
@transaction.atomic
def consulta_buro(request):
    try:
        data = request.data
        serializer = ConsultaBuroSerializer(data=data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            identificacion = validated_data.get("identificacion")
            tipo_identificacion = validated_data.get("tipo_identificacion")

            # consultar al servicio de equifax ---------------------
            json_res = EquifaxAPIHelper.request_score(
                identificacion=identificacion,
                tipo_identificacion=tipo_identificacion,
                environment=STAGE,
            )
            sanitized_data = SanitizeEquifaxDataHelper.transform_object(
                json_res)

            # guardar en la base de datos ---------------------
            instance = serializer.save(
                response_data=sanitized_data,
            )

            res_serializer = ConsultaBuroResponseSerializer(instance)
            return Response({
                'status': status.HTTP_201_CREATED,
                'message': 'Elemento creado',
                'data': res_serializer.data
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return handle_rest_exception_helper(e)
