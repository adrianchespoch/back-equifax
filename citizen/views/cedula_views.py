from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db import transaction
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import status
from citizen.models.cedula_model import Cedula

from citizen.serializers.cedula_serializers import CedulaSerializer, CedulaResponseSerializer
from backend.shared.helpers.handle_rest_exception_helper import handle_rest_exception_helper
from citizen.helpers.registro_civil_helper import RegistroCivilHelper
from citizen.helpers.citizen_mapper import CedulaMapper


# ## docs openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from backend.shared.views.general_view import GeneralAPIView, GeneralDetailAPIView
from backend.shared.constants.constants import page_size_openapi, page_openapi
from backend.shared.serializers.serializers import (
    BadRequestSerializerDoc,
    NotFoundSerializer,
)

from citizen.filters.cedula_filters import CedulaFilter
from citizen.models.cedula_model import Cedula
from citizen.serializers.cedula_serializers import (
    CedulaSerializer,
    CedulaQueryDocWrapperSerializer,
    CedulaResponseSerializer,
    CedulaFilterSerializer,
    CedulaOptDocSerializer,
    ConsultaCedulaSerializer,
)


class CedulaView(GeneralAPIView):
    model = Cedula
    filter = CedulaFilter

    serializer = CedulaSerializer  # model serializer
    serializer2 = CedulaResponseSerializer  # response

    @swagger_auto_schema(
        operation_description="Get All Cedulas",
        responses={
            200: openapi.Response("OK", CedulaQueryDocWrapperSerializer),
        },
        query_serializer=CedulaFilterSerializer,
        manual_parameters=[page_size_openapi, page_openapi],
    )
    def get(self, request):
        return super().get(request)

    @swagger_auto_schema(
        operation_description="Create Cedula",
        request_body=CedulaSerializer,
        responses={
            201: openapi.Response("OK", CedulaOptDocSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializerDoc),
        },
    )
    def post(self, request):
        return super().post(request)


class CedulaDetailView(GeneralDetailAPIView):
    model = Cedula

    serializer = CedulaSerializer
    serializer2 = CedulaResponseSerializer

    @swagger_auto_schema(
        operation_description="Get Cedula by ID",
        responses={
            200: openapi.Response("OK", CedulaResponseSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
        },
    )
    def get(self, request, pk):
        return super().get(request, pk)

    @swagger_auto_schema(
        operation_description="Update Cedula",
        request_body=CedulaSerializer,
        responses={
            200: openapi.Response("OK", CedulaOptDocSerializer),
            404: openapi.Response("Not Found", NotFoundSerializer),
            400: openapi.Response("Bad Request", BadRequestSerializerDoc),
        },
    )
    def patch(self, request, pk):
        return super().patch(request, pk)

    @swagger_auto_schema(
        operation_description="Delete Cedula",
        responses={
            204: openapi.Response("Ok - No Content"),
            404: openapi.Response("Not Found", NotFoundSerializer),
        },
    )
    def delete(self, request, pk):
        return super().delete(request, pk)


# =====================================
@swagger_auto_schema(
    method="post",
    operation_description="Get Person by Cedula",
    request_body=ConsultaCedulaSerializer,
    responses={
        200: openapi.Response("OK", CedulaResponseSerializer),
        404: openapi.Response("Not Found", NotFoundSerializer),
    },
)
@api_view(["POST"])
@transaction.atomic
def get_person_by_cedula(request):
    try:
        data = request.data
        serializer = ConsultaCedulaSerializer(data=data)
        valid_until = timezone.now() + relativedelta(months=1)

        if serializer.is_valid():
            cedula_input = serializer.validated_data.get("cedula").strip()

            # find in BD -----------------------------------
            registro = Cedula.objects.filter(
                identificacion=cedula_input).order_by('-created_at').first()
            if registro:
                if registro.fechaLimitRefetch < timezone.now():
                    # validate limit date ---------
                    json_res = RegistroCivilHelper.get_persona(cedula_input)
                    mapped_data = CedulaMapper.map_response_to_data(
                        json_res, fechaLimitRefetch=valid_until.strftime(
                            "%Y-%m-%d")
                    )

                    registro.response_data = mapped_data
                    registro.raw_data = json_res
                    registro.fechaLimitRefetch = valid_until
                    registro.save()
                    serializer_out = CedulaResponseSerializer(registro)
                    output = serializer_out.data
                    output["consultaExterna"] = True
                else:
                    serializer_out = CedulaResponseSerializer(registro)
                    output = serializer_out.data
                    output["consultaExterna"] = False

                print("--------- Registro encontrado en BD ---------")
                return Response({
                    "status": status.HTTP_200_OK,
                    "message": "Registro encontrado",
                    "data": output
                }, status=status.HTTP_200_OK)

            # No existe en BD: consultar el servicio externo
            json_res = RegistroCivilHelper.get_persona(cedula_input)
            mapped_data = CedulaMapper.map_response_to_data(
                json_res, fechaLimitRefetch=valid_until.strftime("%Y-%m-%d")
            )

            # create Cedula based on mapped data
            serializer = CedulaSerializer(data=mapped_data)
            if serializer.is_valid():
                instance = serializer.save()

                serializer_out = CedulaResponseSerializer(instance)
                output = serializer_out.data
                output["consultaExterna"] = True

                print("--------- Registro consultado/creado ---------")
                return Response({
                    "status": status.HTTP_201_CREATED,
                    "message": "Registro creado",
                    "data": output
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Datos inválidos",
                    "errors": serializer.errors.items()
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Datos inválidos",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return handle_rest_exception_helper(e)
