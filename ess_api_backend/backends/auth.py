from django.contrib.auth.backends import BaseBackend
from ess_api_backend.models import User  # import your custom User model here
import logging


class ESSApiBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
