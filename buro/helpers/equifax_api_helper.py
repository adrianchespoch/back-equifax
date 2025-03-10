import requests
from requests.exceptions import Timeout

from backend.settings import (
    EQUIFAX_SERVICE_API_URL,
    EQUIFAX_API_USERNAME,
    EQUIFAX_API_PASSWORD,
)
from backend.shared.exceptions.custom_generic_exception import CustomGenericException


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
            )
            response.raise_for_status()
            return response.json()
        except Timeout:
            raise CustomGenericException(
                message='El servicio de Equifax está tardando demasiado en responder, por favor intente más tarde',
                status=504)
        except Exception as e:
            raise CustomGenericException(
                detail=f"Error al autenticar con el servicio de Equifax: {e}",
                status_code=504,
            )

    @staticmethod
    def authenticate_dev():
        try:
            response = requests.get(
                f"{EQUIFAX_SERVICE_API_URL}/get-token",
            )
            response.raise_for_status()
            return response.json()["token"]
        except Timeout:
            raise CustomGenericException(
                message='El servicio de Equifax está tardando demasiado en responder, por favor intente más tarde',
                status=504)
        except Exception as e:
            raise CustomGenericException(
                detail=f"Error al autenticar con el servicio de Equifax: {e}",
                status_code=504,
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
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()
                return response.json()
            else:
                token = EquifaxAPIHelper.authenticate_dev()
                url = f"{EQUIFAX_SERVICE_API_URL}/get-default-score?numeroDocumento={identificacion}&tipoDocumento={tipo_identificacion}&tipoModelo=Score Servicios"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response.json()

        except Timeout:
            raise CustomGenericException(
                message='El servicio de Equifax está tardando demasiado en responder, por favor intente más tarde',
                status=504)
        except Exception as e:
            raise CustomGenericException(
                detail=f"Error al obtener el score de Equifax: {e}",
                status_code=504,
            )
