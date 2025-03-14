from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class UserDB(AbstractUser):
    name = models.CharField(max_length=255, null=False, verbose_name="Full Name")  # Full Name
    email = models.EmailField(unique=True, null=False, verbose_name="Email Address")  # Unique Email
    mobile_number = models.CharField(max_length=15, unique=True, null=False, verbose_name="Mobile Number")  # Phone
    address = models.TextField(blank=True, null=True, verbose_name="Address")  # Optional Address
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name="Profile Picture")  # Profile Pic
    age = models.IntegerField(blank=True, null=True, verbose_name="Age")  # Age
    sex = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        blank=True,
        verbose_name="Gender"
    )  # Gender

    is_staff = models.BooleanField(default=False, verbose_name="Admin Privileges")  # Admin Role
    is_active = models.BooleanField(default=True, verbose_name="Account Status")  # Active/Inactive
    date_joined = models.DateTimeField(default=now, verbose_name="Account Creation Date")  # Auto Timestamp

    USERNAME_FIELD = 'username'  # Ensures username is primary for login
    REQUIRED_FIELDS = ['email', 'mobile_number', 'name']  # Required Fields at Signup

    def __str__(self):
        return self.username
