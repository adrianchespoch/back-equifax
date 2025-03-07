from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from dateutil.relativedelta import relativedelta


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
    ConsultaEQUIFAXSerializer,
)

from buro.helpers.sanitize_equifax_data_helper import SanitizeEquifaxDataHelper
from buro.helpers.equifax_api_helper import EquifaxAPIHelper
from backend.settings import (
    EQUIFAX_API_INTERVAL_MESES,
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
    request_body=ConsultaEQUIFAXSerializer,
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
        serializer = ConsultaEQUIFAXSerializer(data=data)
        valid_until = timezone.now() + relativedelta(months=EQUIFAX_API_INTERVAL_MESES)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            identificacion = validated_data.get("identificacion")
            tipo_identificacion = validated_data.get("tipo_identificacion")
            schema_name = validated_data.get("schema_name")
            empresa_uuid = validated_data.get("empresa_uuid")

            # consultar en la base de datos ---------------------
            consulta = ConsultaBuro.objects.filter(
                identificacion=identificacion,
                tipo_identificacion=tipo_identificacion,
                schema_name=schema_name,
                empresa_uuid=empresa_uuid,
            ).order_by('-created_at').first()
            if consulta is not None:
                # check valid_until -------------
                if consulta.valid_until is not None and consulta.valid_until < timezone.now():
                    json_res = EquifaxAPIHelper.request_score(
                        identificacion=identificacion,
                        tipo_identificacion=tipo_identificacion,
                        environment=STAGE,
                    )
                    sanitized_data = SanitizeEquifaxDataHelper.transform_object(
                        json_res)

                    # create -------
                    instance = serializer.save(
                        response_data=sanitized_data,
                        raw_data=json_res,
                        valid_until=valid_until
                    )

                    res_serializer = ConsultaBuroResponseSerializer(instance)
                    data = res_serializer.data
                    data['consultaExterna'] = True
                else:
                    res_serializer = ConsultaBuroResponseSerializer(consulta)
                    data = res_serializer.data
                    data['consultaExterna'] = False

                print('--------- Elemento encontrado en la base de datos ---------')
                return Response({
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': data
                }, status=status.HTTP_200_OK)
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
                raw_data=json_res,
                valid_until=valid_until
            )

            res_serializer = ConsultaBuroResponseSerializer(instance)
            data = res_serializer.data
            data['consultaExterna'] = True
            print('--------- Elemento Consultado/Creado ---------')
            return Response({
                'status': status.HTTP_201_CREATED,
                'message': 'Elemento creado',
                'data': data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Datos inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return handle_rest_exception_helper(e)
