from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserDB
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(required=True)
    mobile_number = forms.CharField(required=True)

    class Meta:
        model = UserDB
        fields = ("username", "email", "name", "mobile_number", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserDB.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if UserDB.objects.filter(mobile_number=mobile_number, is_active=True).exists():
            raise ValidationError("A user with this mobile number already exists.")
        return mobile_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.name = self.cleaned_data["name"]
        user.mobile_number = self.cleaned_data["mobile_number"]
        user.is_active = False  # User starts as inactive until email verification
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    class Meta:
        model = UserDB
        fields = ['username', 'password']
