from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# ### Serializers based on Existing Models
from .models import User


# ### Serializer: Python to JSON  &  Deserialize: JSON to Python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields tuple q podran ser consultados (se enviaran en la response del view)
        fields = ["email", "name", "last_name", "id", "avatar"]


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields tuple q podran ser consultados (se enviaran en la response del view)
        fields = ("id", "email", "name", "last_name", "created_at")  # specifying fields
        # fields = '__all__' # all fields


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # ### set fields to jwt payload - how to send user and token instead of access/refresh???
        token = super().get_token(user)
        token["email"] = user.email  # set email in JWT
        token["avatar"] = user.avatar.url
        token["is_staff"] = user.is_staff  # isAdmin?
        token["name"] = user.name
        token["last_name"] = user.last_name
        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except InvalidToken:
            raise AuthenticationFailed("Invalid token")
        except Exception as e:
            raise AuthenticationFailed(
                "There was a problem logging in. Check your email and password or create an account."
            )

        # Customize response data
        data.update(
            {
                "user": {
                    "email": self.user.email,
                    "avatar": self.user.avatar.url,
                    "is_staff": self.user.is_staff,
                    "name": self.user.name,
                    "last_name": self.user.last_name,
                }
            }
        )
        return data
