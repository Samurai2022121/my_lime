from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ("email", "phone_number", "name", "surname")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("email", "phone_number", "name", "surname")
