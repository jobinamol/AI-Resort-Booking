from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserDB, Package, Room
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

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['package_name', 'description', 'price', 'duration', 'package_type', 'amenities', 'image']
        widgets = {
            'package_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'package_type': forms.RadioSelect(choices=[('Staycation', 'Staycation'), ('Daycation', 'Daycation')]),
            'amenities': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero")
        return price

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration <= 0:
            raise forms.ValidationError("Duration must be greater than zero")
        return duration

    def clean_amenities(self):
        amenities = self.cleaned_data.get('amenities')
        if not amenities:
            return ''
        # Clean and format amenities as comma-separated list
        amenities_list = [item.strip() for item in amenities.split(',') if item.strip()]
        return ', '.join(amenities_list)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file size must be less than 5MB")
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("File must be an image")
        return image

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_number', 'room_type', 'floor', 'capacity',
            'base_price', 'current_status', 'amenities',
            'description', 'size_sqft', 'view_type',
            'bed_type', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'amenities': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_base_price(self):
        base_price = self.cleaned_data.get('base_price')
        if base_price and base_price < 0:
            raise forms.ValidationError("Price cannot be negative")
        return base_price

    def clean_room_number(self):
        room_number = self.cleaned_data.get('room_number')
        if not room_number:
            raise forms.ValidationError("Room number is required")
        
        # Check if room number already exists for this resort
        if self.instance.pk:  # If editing existing room
            exists = Room.objects.exclude(pk=self.instance.pk).filter(
                resort=self.instance.resort,
                room_number=room_number
            ).exists()
        else:  # If creating new room
            exists = Room.objects.filter(
                resort=self.instance.resort,
                room_number=room_number
            ).exists()
        
        if exists:
            raise forms.ValidationError("Room number already exists")
        
        return room_number