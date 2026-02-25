"""
Custom Authentication Backend for Email-based login
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom backend that allows authentication using either email or username
    Performs case-insensitive email matching for robustness
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Override Django's default authenticate method to support email-based login
        """
        try:
            # Try to find user by email (case-insensitive) or username
            user = User.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
        except User.DoesNotExist:
            # Run default password hasher to prevent timing attacks
            User().set_password(password)
            return None

        # Check if password is correct
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
