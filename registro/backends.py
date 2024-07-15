# registro/backends.py

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)  # Busca el usuario por email
            if user.check_password(password):  # Verifica la contraseña
                return user  # Devuelve el usuario si la autenticación es exitosa
        except User.DoesNotExist:
            return None  # Devuelve None si no se encuentra el usuario

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)  # Obtiene el usuario por ID
        except User.DoesNotExist:
            return None  # Devuelve None si no se encuentra el usuario
