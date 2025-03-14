from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserDB

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(required=True)
    mobile_number = forms.CharField(required=True)

    class Meta:
        model = UserDB
        fields = ("username", "email", "name", "mobile_number", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.name = self.cleaned_data["name"]
        user.mobile_number = self.cleaned_data["mobile_number"]
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    class Meta:
        model = UserDB
        fields = ['username', 'password']
