from django.shortcuts import render

from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password # hashear password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import IntegrityError

from .models import User
from .serializers import MyTokenObtainPairSerializer, RegisterUserSerializer
from .dto import ErrorResponseDTO, SuccessResponseDTO




@api_view(['POST'])
def register(request):
    try:
        data = request.data
        user = User.objects.create(
            email=data['email'],
            name=data['name'],
            last_name=data['last_name'],
            password=make_password(data['password']),
        )
        serializer = RegisterUserSerializer(user, many = False)
        response_dto = SuccessResponseDTO(status=200, data=serializer.data, message='User created')
        return Response(response_dto.__dict__, status=200)
    except IntegrityError:
        response_dto = ErrorResponseDTO(status=400, error='Email already exists')
        return Response(response_dto.__dict__, status=400)
    except KeyError:
        # barrer todos los campos q faltan y retornarlos en el response como array
        missing_fields = []
        for field in RegisterUserSerializer.Meta.fields:
            if field not in data:
                missing_fields.append(
                    f'{field.replace("_", " ").capitalize()} es requerido'
                )
        response_dto = ErrorResponseDTO(status=400, error='Missing fields', missing_fields=missing_fields)
        return Response(response_dto.__dict__, status=400)


# ## esta view permite hacer login: returns access & refresh token
class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

