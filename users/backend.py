from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.hashers import check_password

User = get_user_model()

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:

            user = User.objects.get(Q(email=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
