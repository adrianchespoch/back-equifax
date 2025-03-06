import unicodedata
import re


class SanitizeEquifaxDataHelper:
    """
    Helper para sanitizar y transformar la data de la API externa.

    La transformación realiza:
      - En el primer nivel: se quitan acentos, se reemplazan espacios por guiones bajos y se convierte a mayúsculas.
      - En niveles anidados: se transforman las keys a camelCase.
      - Se sanitiza el valor de 'planSugerido' dentro de la sección 'PLAN_SUGERIDO'.

    Ejemplo de uso:
        sanitized_data = DataSanitizerHelper.sanitize(api_response)
    """

    @staticmethod
    def remove_accents(input_str: str) -> str:
        """Elimina acentos de una cadena."""
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    @staticmethod
    def sanitize_value(value):
        """Si el valor es una cadena, lo convierte a ASCII (eliminando caracteres no ASCII) y recorta espacios."""
        if isinstance(value, str):
            return value.encode('ascii', 'ignore').decode('ascii').strip()
        return value

    @staticmethod
    def sanitize_key_nested(key: str) -> str:
        """
        Transforma una key anidada a camelCase.
        Ejemplo: "Código de Consulta" -> "codigoDeConsulta"
        """
        # Elimina acentos y quita caracteres no alfanuméricos (excepto espacios)
        key_clean = SanitizeEquifaxDataHelper.remove_accents(key)
        key_clean = re.sub(r'[^A-Za-z0-9 ]+', '', key_clean)
        parts = key_clean.split()
        if not parts:
            return key_clean
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    @staticmethod
    def transform_object(obj, level: int = 0):
        """
        Transforma recursivamente las keys y valores del objeto.
          - Nivel 0: keys se sanitizan quitando acentos, reemplazando espacios por guiones bajos y convirtiendo a mayúsculas.
          - Niveles anidados: se convierte a camelCase.
        """
        if isinstance(obj, dict):
            new_obj = {}
            for key, value in obj.items():
                if level == 0:
                    new_key = SanitizeEquifaxDataHelper.remove_accents(
                        key).replace(" ", "_").upper()
                else:
                    new_key = SanitizeEquifaxDataHelper.sanitize_key_nested(
                        key)
                new_obj[new_key] = SanitizeEquifaxDataHelper.transform_object(
                    value, level=level+1)
            return new_obj
        elif isinstance(obj, list):
            return [SanitizeEquifaxDataHelper.transform_object(item, level=level) for item in obj]
        else:
            return SanitizeEquifaxDataHelper.sanitize_value(obj)

    @staticmethod
    def transform_plan_sugerido(plan_list):
        """
        Procesa la lista de elementos en PLAN_SUGERIDO, sanitizando el valor del key 'planSugerido'
        y corrigiéndolo a "BASICO" si coincide con el patrón.
        """
        new_list = []
        for item in plan_list:
            # Se asume que la key ya fue transformada a camelCase (planSugerido)
            if "planSugerido" in item:
                val = SanitizeEquifaxDataHelper.sanitize_value(
                    item["planSugerido"])
                # Si el valor coincide con un patrón similar a "B    SICO" (ignorando espacios y mayúsculas/minúsculas)
                if re.match(r'^B\s*SICO$', val, flags=re.IGNORECASE):
                    item["planSugerido"] = "BASICO"
                else:
                    item["planSugerido"] = val
            new_list.append(item)
        return new_list

    @staticmethod
    def sanitize(data: dict) -> dict:
        """
        Función principal para sanitizar y transformar la data.
          - Transforma todas las keys y valores.
          - Aplica la transformación especial para la sección PLAN_SUGERIDO.
        """
        transformed = SanitizeEquifaxDataHelper.transform_object(data)
        if "PLAN_SUGERIDO" in transformed and isinstance(transformed["PLAN_SUGERIDO"], list):
            transformed["PLAN_SUGERIDO"] = SanitizeEquifaxDataHelper.transform_plan_sugerido(
                transformed["PLAN_SUGERIDO"])
        return transformed
