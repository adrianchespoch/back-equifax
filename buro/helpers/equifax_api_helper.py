import requests
from requests.exceptions import Timeout

from backend.settings import (
    EQUIFAX_SERVICE_API_URL,
    EQUIFAX_API_USERNAME,
    EQUIFAX_API_PASSWORD,
)
from backend.shared.exceptions.custom_generic_exception import CustomGenericException
from backend.shared.exceptions.bad_request_exception import BadRequestException
from requests.exceptions import HTTPError


class EquifaxAPIHelper:

    # ### AUTHENTICATION ----------------------------
    @staticmethod
    def authenticate():
        try:
            response = requests.post(
                f"{EQUIFAX_SERVICE_API_URL}/login/authenticate",
                json={
                    "Username": EQUIFAX_API_USERNAME,
                    "Password": EQUIFAX_API_PASSWORD,
                },
                timeout=36,
            )
            response.raise_for_status()
            return response.json()
        except Timeout:
            raise CustomGenericException(
                message='El servicio de Equifax está tardando demasiado en responder, por favor intente más tarde',
                status=504)
        except Exception as e:
            raise CustomGenericException(
                message=f"Error al autenticar con el servicio de Equifax: {e}",
                status=504,
            )

    @staticmethod
    def authenticate_dev():
        try:
            response = requests.get(
                f"{EQUIFAX_SERVICE_API_URL}/get-token",
                timeout=36,
            )
            response.raise_for_status()
            return response.json()["token"]
        except Timeout:
            raise CustomGenericException(
                message='El servicio de Equifax está tardando demasiado en responder, por favor intente más tarde',
                status=504)
        except Exception as e:
            raise CustomGenericException(
                message=f"Error al autenticar con el servicio de Equifax: {e}",
                status=504,
            )

    # ### CONSULTAS ----------------------------
    @staticmethod
    def request_score(identificacion: str, tipo_identificacion: str, environment: str):
        try:
            if environment == "prod":
                token = EquifaxAPIHelper.authenticate()
                url = f"{EQUIFAX_SERVICE_API_URL}/ServicioBuro/COMM/resultadoModelo"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
                data = {
                    "numeroDocumento": identificacion,
                    "tipoDocumento": tipo_identificacion,
                    "tipoModelo": "Score Servicios",
                }
                response = requests.post(
                    url, json=data, headers=headers, timeout=36)
                response.raise_for_status()
                return response.json()
            else:
                token = EquifaxAPIHelper.authenticate_dev()
                url = f"{EQUIFAX_SERVICE_API_URL}/get-default-score?numeroDocumento={identificacion}&tipoDocumento={tipo_identificacion}&tipoModelo=Score Servicios"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
                response = requests.get(url, headers=headers, timeout=36)
                if response.status_code == 400:
                    err_msg = response.json().get('error', 'Datos inválidos')
                    raise BadRequestException(message=err_msg)
                response.raise_for_status()
                return response.json()

        except HTTPError as http_err:
            raise CustomGenericException(
                message=f"{http_err}",
                status=504,
            )
        except Timeout:
            raise CustomGenericException(
                message='El servicio de Equifax está tardando demasiado en responder, por favor intente más tarde',
                status=504)
        except Exception as e:
            if isinstance(e, BadRequestException):
                raise CustomGenericException(
                    message=f"{e}",
                    status=400,
                )
            raise CustomGenericException(
                message=f"Error al obtener el score de Equifax: {e}",
                status=504,
            )
