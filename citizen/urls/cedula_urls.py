from django.urls import path

from citizen.views.cedula_views import (
    CedulaView,
    CedulaDetailView,
    get_person_by_cedula,
)


urlpatterns = [
    path("", CedulaView.as_view(), name="cedula"),

    path("consulta/", get_person_by_cedula,
         name="get_person_by_cedula"),

    path("<int:pk>/", CedulaDetailView.as_view(), name="cedula-detail"),
]
