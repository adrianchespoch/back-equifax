"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


# ### Swagger
import os
from rest_framework import permissions
from django.urls import path, re_path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=os.environ.get('API_URL')
)

urlpatterns = [
    # ### Swagger
    re_path(r'^externo-consultas/v1/swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('externo-consultas/v1/swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('externo-consultas/v1/redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),


    # ### Admin
    path('externo-consultas/v1/admin/', admin.site.urls),


    # ### API
    # ## set v1 as version: no se puede colocar 1 prefix generico como en spring o nestjs
    path('externo-consultas/v1/users/', include('users.urls')),

    path("externo-consultas/v1/consulta-buro/", include("buro.urls.consulta_buro_urls")),

    path("api/v1/cedula/", include("citizen.urls.cedula_urls")),

]
