from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now, timedelta
from django.core.exceptions import ValidationError
import random


class UserDB(AbstractUser):
    name = models.CharField(max_length=255, null=False, verbose_name="Full Name")  # Full Name
    email = models.EmailField(verbose_name="Email Address")  # Email field
    mobile_number = models.CharField(max_length=15, verbose_name="Mobile Number")  # Mobile number field
    address = models.TextField(blank=True, null=True, verbose_name="Address")  # Optional Address
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name="Profile Picture")  # Profile Pic
    age = models.IntegerField(blank=True, null=True, verbose_name="Age")  # Age
    sex = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female')],
        blank=True,
        verbose_name="Gender"
    )  # Gender
    designation = models.CharField(
        max_length=50,
        choices=[
            ('owner', 'Resort Owner'),
            ('manager', 'Resort Manager'),
        ],
        default='manager'
    )
    is_approved = models.BooleanField(default=False, verbose_name="Admin Approved")
    is_staff = models.BooleanField(default=False, verbose_name="Admin Privileges")  # Admin Role
    is_active = models.BooleanField(default=True, verbose_name="Account Status")  # Changed default to True
    date_joined = models.DateTimeField(default=now, verbose_name="Account Creation Date")  # Auto Timestamp

    USERNAME_FIELD = 'username'  # Ensures username is primary for login
    REQUIRED_FIELDS = ['email', 'mobile_number', 'name', 'designation']  # Required Fields at Signup

    def __str__(self):
        return self.username

class Resort(models.Model):
    user = models.OneToOneField(UserDB, on_delete=models.CASCADE, related_name='resort')
    resort_name = models.CharField(max_length=255, null=False, verbose_name="Resort Name")
    resort_address = models.TextField(null=False, verbose_name="Resort Address")
    resort_contact = models.CharField(max_length=15, null=False, verbose_name="Resort Contact")
    resort_email = models.EmailField(verbose_name="Resort Email", blank=True, null=True)
    resort_website = models.URLField(verbose_name="Resort Website", blank=True, null=True)
    resort_description = models.TextField(verbose_name="Resort Description", blank=True, null=True)
    resort_type = models.CharField(
        max_length=50,
        choices=[
            ('beach_resort', 'Beach Resort'),
            ('mountain_resort', 'Mountain Resort'),
            ('lake_resort', 'Lake Resort'),
            ('forest_resort', 'Forest Resort'),
            ('desert_resort', 'Desert Resort'),
            ('island_resort', 'Island Resort'),
            ('wellness_resort', 'Wellness Resort'),
            ('golf_resort', 'Golf Resort'),
            ('ski_resort', 'Ski Resort'),
            ('eco_resort', 'Eco Resort'),
            ('luxury_resort', 'Luxury Resort'),
            ('family_resort', 'Family Resort'),
            ('boutique_resort', 'Boutique Resort'),
            ('all_inclusive', 'All-Inclusive Resort'),
            ('casino_resort', 'Casino Resort'),
            ('theme_park_resort', 'Theme Park Resort'),
            ('villa_resort', 'Villa Resort'),
            ('business_resort', 'Business Resort'),
            ('adventure_resort', 'Adventure Resort'),
            ('heritage_resort', 'Heritage Resort')
        ],
        null=False,
        verbose_name="Resort Type"
    )
    room_count = models.PositiveIntegerField(null=False, verbose_name="Number of Rooms")
    check_in_time = models.TimeField(verbose_name="Check-in Time", null=True, blank=True)
    check_out_time = models.TimeField(verbose_name="Check-out Time", null=True, blank=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Starting Price")
    
    # Basic Facilities
    has_pool = models.BooleanField(default=False, verbose_name="Swimming Pool")
    has_spa = models.BooleanField(default=False, verbose_name="Spa & Wellness")
    has_restaurant = models.BooleanField(default=False, verbose_name="Restaurant")
    has_gym = models.BooleanField(default=False, verbose_name="Fitness Center")
    has_wifi = models.BooleanField(default=False, verbose_name="High-Speed Wi-Fi")
    has_parking = models.BooleanField(default=False, verbose_name="Valet Parking")

    # Staycation Packages
    has_romantic_package = models.BooleanField(default=False, verbose_name="Romantic Getaway")
    has_family_package = models.BooleanField(default=False, verbose_name="Family Vacation")
    has_business_package = models.BooleanField(default=False, verbose_name="Business Stay")
    has_wellness_package = models.BooleanField(default=False, verbose_name="Wellness Retreat")
    has_longstay_package = models.BooleanField(default=False, verbose_name="Extended Stay")
    has_workation_package = models.BooleanField(default=False, verbose_name="Work From Resort")

    # Daycation Packages
    has_pool_access = models.BooleanField(default=False, verbose_name="Pool Day Pass")
    has_spa_day = models.BooleanField(default=False, verbose_name="Spa Day Package")
    has_dining = models.BooleanField(default=False, verbose_name="Dining Experience")
    has_workspace = models.BooleanField(default=False, verbose_name="Day Workspace")

    # Venue Functions
    has_wedding_venue = models.BooleanField(default=False, verbose_name="Wedding Venue")
    has_conference_hall = models.BooleanField(default=False, verbose_name="Conference Hall")
    has_banquet_hall = models.BooleanField(default=False, verbose_name="Banquet Hall")
    has_outdoor_venue = models.BooleanField(default=False, verbose_name="Outdoor Events")

    # Adventure & Activities
    has_water_sports = models.BooleanField(default=False, verbose_name="Water Sports")
    has_trekking = models.BooleanField(default=False, verbose_name="Trekking Tours")
    has_cycling = models.BooleanField(default=False, verbose_name="Cycling")
    has_yoga = models.BooleanField(default=False, verbose_name="Yoga Classes")
    has_cooking_class = models.BooleanField(default=False, verbose_name="Cooking Classes")
    has_kids_club = models.BooleanField(default=False, verbose_name="Kids Club")

    # Transportation Services
    has_airport_transfer = models.BooleanField(default=False, verbose_name="Airport Transfer")
    has_car_rental = models.BooleanField(default=False, verbose_name="Car Rental")
    has_shuttle = models.BooleanField(default=False, verbose_name="Shuttle Service")
    has_taxi = models.BooleanField(default=False, verbose_name="Taxi Booking")

    # Special Category Packages
    has_student_package = models.BooleanField(default=False, verbose_name="Student Groups")
    has_senior_package = models.BooleanField(default=False, verbose_name="Senior Citizens")
    has_corporate_package = models.BooleanField(default=False, verbose_name="Corporate Groups")
    has_honeymoon_package = models.BooleanField(default=False, verbose_name="Honeymoon")

    # Additional Services
    has_laundry = models.BooleanField(default=False, verbose_name="Laundry Service")
    has_childcare = models.BooleanField(default=False, verbose_name="Childcare")
    has_room_service = models.BooleanField(default=False, verbose_name="24/7 Room Service")
    has_concierge = models.BooleanField(default=False, verbose_name="Concierge")
    has_medical = models.BooleanField(default=False, verbose_name="Medical Assistance")
    is_pet_friendly = models.BooleanField(default=False, verbose_name="Pet Friendly")

    # Resort Images
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.resort_name} - {self.get_resort_type_display()}"

    def clean(self):
        # Add validation logic
        if self.check_in_time and self.check_out_time and self.check_in_time >= self.check_out_time:
            raise ValidationError("Check-out time must be after check-in time")
        
        if self.min_price and self.min_price < 0:
            raise ValidationError("Price cannot be negative")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Resort'
        verbose_name_plural = 'Resorts'
        ordering = ['resort_name']  # Add default ordering

class ResortImage(models.Model):
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='resort_images/', verbose_name="Resort Image")
    caption = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-uploaded_at']

    def __str__(self):
        return f"{self.resort.resort_name} - {self.caption or 'Image'}"
