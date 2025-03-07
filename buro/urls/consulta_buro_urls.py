from django.urls import path

from buro.views.consulta_buro_views import (
    ConsultaBuroView,
    ConsultaBuroDetailView,

    consulta_buro,
)


urlpatterns = [
    path("", ConsultaBuroView.as_view(), name="consulta_buro"),

    path("equifax/", consulta_buro, name="consulta_buro-equifax"),

    path("<uuid:pk>/", ConsultaBuroDetailView.as_view(),
         name="consulta_buro-detail"),
]
