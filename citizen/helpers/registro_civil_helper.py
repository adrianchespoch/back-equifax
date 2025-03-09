import requests
from requests.exceptions import HTTPError, Timeout, RequestException
from backend.settings import REGISTRO_CIVIL_API_URL
from backend.shared.exceptions.custom_generic_exception import CustomGenericException


class RegistroCivilHelper:
    @staticmethod
    def get_persona(cedula: str) -> dict:
        url = f"{REGISTRO_CIVIL_API_URL}/{cedula}"
        try:
            response = requests.get(url, verify=True, timeout=30)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            raise CustomGenericException(
                message=f"Error HTTP consultando Registro Civil: {http_err}", status=response.status_code)
        except Timeout:
            raise CustomGenericException(
                message="El servicio de Registro Civil está tardando demasiado en responder, por favor intente más tarde", status=504)
        except RequestException as req_err:
            raise CustomGenericException(
                message=f"Error consultando Registro Civil: {req_err}", status=500)
        except Exception as e:
            raise CustomGenericException(
                message=f"Error inesperado consultando Registro Civil: {e}", status=500)
