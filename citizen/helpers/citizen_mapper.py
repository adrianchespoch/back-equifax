import uuid

from backend.shared.utils.common_utils import calculate_citizen_age


class CedulaMapper:
    @staticmethod
    def map_response_to_data(response: dict, fechaLimitRefetch: str) -> dict:

        data = response.get("response", {})
        identificacion = data.get("NUI", "").strip()
        fullName = data.get("Nombre", "").strip()
        nacionalidad = data.get("Nacionalidad", "").strip()
        condicion = data.get("CondicionCedulado", "").strip()
        fechaNacimiento = data.get("FechaNacimiento", "").strip()
        edad = calculate_citizen_age(fechaNacimiento)
        esTerceraEdad = edad >= 65

        return {
            "id": str(uuid.uuid4()),
            "identificacion": identificacion,
            "tipo_identificacion": "CEDULA",
            "fullName": fullName,
            "nacionalidad": nacionalidad,
            "condicionCedulado": condicion,
            "esDiscapacitado": "DISCAPACI" in condicion.upper(),
            "fechaNacimiento": fechaNacimiento,
            "esTerceraEdad": esTerceraEdad,
            "edad": edad,

            # Campos opcionales
            "nombreMadre": data.get("NombreMadre", "").strip() or None,
            "nombrePadre": data.get("NombrePadre", "").strip() or None,
            "numeroCasa": data.get("NumeroCasa", "").strip() or None,
            "profesion": data.get("Profesion", "").strip() or None,
            "sexo": data.get("Sexo", "").strip() or None,
            "calle": data.get("Calle", "").strip() or None,
            "lugarNacimiento": data.get("LugarNacimiento", "").strip() or None,
            "codigoError": data.get("CodigoError", "").strip() or None,
            "conyuge": data.get("Conyuge", "").strip() or None,
            "domicilio": data.get("Domicilio", "").strip() or None,
            "error": data.get("Error", "").strip() or None,
            "estadoCivil": data.get("EstadoCivil", "").strip() or None,
            "genero": data.get("Genero", "").strip() or None,
            "instruccion": data.get("Instruccion", "").strip() or None,
            "lugarInscripcionGenero": data.get("LugarInscripcionGenero", "").strip() or None,
            "fechaCedulacion": data.get("FechaCedulacion", "").strip() or None,
            "fechaInscripcionDefuncion": data.get("FechaInscripcionDefuncion", "").strip() or None,
            "fechaInscripcionGenero": data.get("FechaInscripcionGenero", "").strip() or None,
            "fechaLimitRefetch": fechaLimitRefetch,
        }
