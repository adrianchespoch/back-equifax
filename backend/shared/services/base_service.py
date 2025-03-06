from django.core.paginator import Paginator
from django.core.paginator import EmptyPage, PageNotAnInteger

from backend.shared.constants.constants import (
    PAGINATION_DEFAULT_PAGE_NUMBER,
    PAGINATION_DEFAULT_PAGE_SIZE,
)
from backend.shared.exceptions.invalid_fields_exception import InvalidFieldsException
from backend.shared.exceptions.resource_not_found_exception import (
    ResourceNotFoundException,
)


class BaseService:

    filter = None
    serializer = None  # model serializer
    serializer2 = None  # response

    def __init__(self, repository):
        self.repository = repository

    # ## main methods =================
    def find_all(
        self,
        filter_params=None,
        page_number=PAGINATION_DEFAULT_PAGE_NUMBER,
        page_size=PAGINATION_DEFAULT_PAGE_SIZE,
    ):
        queryset = self.repository.find_all()

        # filter
        if filter_params:
            queryset = self.filter(filter_params, queryset=queryset).qs

        # pagination
        paginator = Paginator(queryset, page_size)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = []

        if isinstance(page_obj, list):
            next_page = previous_page = None
            count = total_pages = 0
        else:
            next_page = page_obj.next_page_number() if page_obj.has_next() else None
            previous_page = (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            )
            count = paginator.count
            total_pages = paginator.num_pages

        # serializer
        serializer = self.serializer2(page_obj, many=True)
        return {
            "meta": {
                "next": next_page,
                "previous": previous_page,
                "count": count,
                "total_pages": total_pages,
            },
            "data": serializer.data,
        }

    def find_one(self, pk) -> dict:
        instance = self.get_by_id(pk)
        return self.serializer2(instance).data

    def create(self, data) -> dict:
        serializer = self.serializer(data=data)
        if serializer.is_valid():
            model_instance = self.repository.create(serializer.validated_data)
            return self.serializer(model_instance).data  # xq quiero el id
        raise InvalidFieldsException(
            message="Bad Request", fields=serializer.errors.items()
        )

    def update(self, pk, data) -> dict:
        instance = self.get_by_id(pk)
        serializer = self.serializer(instance, data=data, partial=True)
        if serializer.is_valid():
            instance = self.repository.update(pk, serializer.validated_data)
            return self.serializer(instance).data
        else:
            raise InvalidFieldsException(
                message="Invalid fields", fields=serializer.errors.items()
            )

    def delete(self, instance_id) -> bool:
        was_deleted = self.repository.delete(instance_id)
        if not was_deleted:
            raise ResourceNotFoundException(
                message=f"Resource with id '{instance_id}' not found"
            )
        return was_deleted

    # ## auxiliar methods =================
    def get_by_id(self, pk) -> object:
        instance = self.repository.find_one(pk)
        if not instance:
            raise ResourceNotFoundException(
                message=f"Resource with id '{pk}' not found"
            )
        return instance
