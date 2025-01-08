from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Check if user exists by username or email
        try:
            user = User.objects.get(username=username) if User.objects.filter(username=username).exists() else User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
