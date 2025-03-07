from abc import ABC, abstractmethod
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from backend.shared.helpers.handle_rest_exception_helper import (
    handle_rest_exception_helper,
)

# cache ---------
from django.core.cache import cache
from backend.shared.utils.common_utils import generate_cache_key, clear_cache_key_get_all, generate_cache_key_generic_one_field
from backend.settings import REDIS_TIMEOUT


class CacheViewMixin:
    def get_cache_key(self, filter_params):
        return generate_cache_key(filter_params=filter_params, model_name=self.service.repository.model.__name__)

    def get_cached_data(self, cache_key):
        return cache.get(cache_key)

    def set_cached_data(self, cache_key, data):
        cache.set(cache_key, data, timeout=int(REDIS_TIMEOUT))

    def clear_cache(self, schema_name=None, model_name=None):
        repo_model_name = None
        if hasattr(self.service, 'repository') and self.service.repository:
            repo_model_name = self.service.repository.model.__name__
        model_name = model_name if model_name else repo_model_name
        cache.delete(f"{model_name}___all")
        cache.delete(f"{model_name}___one")
        clear_cache_key_get_all(model_name)
        self.clear_find_one_related_cache(schema_name)

    def clear_model_related_cache(self, model_name):
        cache.delete_pattern(f"{model_name}*")

    def clear_find_one_related_cache(self, schema_name):
        cache.delete_pattern(f"*{schema_name}*___one")
        cache.delete_pattern(f"*{schema_name}*___one")


class GenericFindOneFieldViewMixinCache(CacheViewMixin):
    def get_mx(self, request, field=None, cache_key=None, model_name=None):
        try:
            filter_params = request.GET

            if cache_key is None:
                cache_key_x = cache_key if cache_key else generate_cache_key_generic_one_field(
                    field, model_name, filter_params)
                cache_data = self.get_cached_data(cache_key_x)

                if cache_data:
                    print('-------------- CACHE ----------------')
                    return Response(
                        {
                            'status': status.HTTP_200_OK,
                            'message': 'Elemento encontrado',
                            'data': cache_data
                        },
                        status=status.HTTP_200_OK
                    )

            serialized = self.generic_find_one_field_method(
                request, field, cache_key, model_name, filter_params)
            self.set_cached_data(cache_key_x, serialized)
            print('-------------- DB ----------------')
            return Response(
                {
                    'status': status.HTTP_200_OK,
                    'message': 'Elemento encontrado',
                    'data': serialized
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_rest_exception_helper(e)
