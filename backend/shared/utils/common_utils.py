import json
import hashlib
from django.core.cache import cache


# ### REDIS ==========================
def generate_cache_key(filter_params, model_name):
    """
    Generates a unique cache key based on the filter parameters.
    hash md5: the same input will always produce the same output.
    """
    filter_string = json.dumps(filter_params, sort_keys=True)
    return f"{model_name}___all___{hashlib.md5(filter_string.encode()).hexdigest()}"


def clear_cache_key_get_all(model_name):
    """Clears the cache key for the get all method."""
    cache.delete_pattern(f"{model_name}___all___*")


def generate_cache_key_generic_one_field(field, model_name, filter_params=None):
    """
    Generates a unique cache key based on the field.
    hash md5: the same input will always produce the same output.
    """
    filter_string = json.dumps(filter_params, sort_keys=True)
    return f"{model_name}_{field}_{hashlib.md5(filter_string.encode()).hexdigest()}__one"


# COMMON UTILS ==========================
def humanize_model_name(model_name):
    # Convierte nombres de modelo tipo CamelCase a una forma más legible.
    return ''.join([' ' + char.lower() if char.isupper() else char for char in model_name]).strip().capitalize()


def format_params(params):
    # Convierte el diccionario de parámetros en una lista separada por comas.
    return ', '.join([f"{key} {value}" for key, value in params.items()])
