from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now, timedelta, timezone
from django.core.exceptions import ValidationError
import random
import json
from decimal import Decimal
from django.db.models import Q
from django.contrib.auth.hashers import make_password, check_password
import os
from django.conf import settings


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
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Average Rating")
    total_reviews = models.PositiveIntegerField(default=0, verbose_name="Total Reviews")
    featured = models.BooleanField(default=False, verbose_name="Featured Resort")
    gallery = models.ManyToManyField('ResortImage', related_name='resort_galleries', blank=True)
    main_image = models.ForeignKey('ResortImage', on_delete=models.SET_NULL, null=True, blank=True, related_name='resort_main_image')
    
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

    def get_occupancy_rate(self):
        """Calculate current occupancy rate"""
        # TODO: Implement actual booking logic
        return 85  # Placeholder

    def get_monthly_revenue(self):
        """Calculate current month's revenue"""
        # TODO: Implement actual booking logic
        return 45678  # Placeholder

    def get_total_guests(self):
        """Get total number of guests"""
        # TODO: Implement actual booking logic
        return 1234  # Placeholder

    def get_average_rating(self):
        """Calculate average rating"""
        # TODO: Implement actual review logic
        return 4.5  # Placeholder

    def get_recent_bookings(self, limit=5):
        """Get recent bookings"""
        # TODO: Implement actual booking logic
        return [
            {
                'guest_name': 'John Doe',
                'check_in': '2024-03-15',
                'check_out': '2024-03-18',
                'status': 'Confirmed',
                'amount': 1200
            }
        ]

    def get_monthly_stats(self):
        """Get monthly statistics for charts"""
        # TODO: Implement actual booking logic
        return {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'revenue': [30000, 35000, 40000, 38000, 42000, 45678],
            'occupancy': [75, 82, 85, 88, 90, 95]
        }

    def get_facility_groups(self):
        """Get grouped facilities for display"""
        return {
            'basic': [
                {'name': 'Swimming Pool', 'available': self.has_pool},
                {'name': 'Spa & Wellness', 'available': self.has_spa},
                {'name': 'Restaurant', 'available': self.has_restaurant},
                {'name': 'Gym', 'available': self.has_gym},
                {'name': 'WiFi', 'available': self.has_wifi},
                {'name': 'Parking', 'available': self.has_parking},
            ],
            'activities': [
                {'name': 'Water Sports', 'available': self.has_water_sports},
                {'name': 'Trekking', 'available': self.has_trekking},
                {'name': 'Cycling', 'available': self.has_cycling},
                {'name': 'Yoga', 'available': self.has_yoga},
            ],
            'services': [
                {'name': 'Room Service', 'available': self.has_room_service},
                {'name': 'Laundry', 'available': self.has_laundry},
                {'name': 'Childcare', 'available': self.has_childcare},
                {'name': 'Medical Services', 'available': self.has_medical},
            ]
        }

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

class ResortAnalytics(models.Model):
    resort = models.OneToOneField(Resort, on_delete=models.CASCADE, related_name='analytics')
    total_bookings = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    peak_season_months = models.JSONField(default=list)
    popular_room_types = models.JSONField(default=dict)
    guest_demographics = models.JSONField(default=dict)
    revenue_by_channel = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    def update_analytics(self):
        # Calculate total bookings and revenue
        bookings = self.resort.bookings.all()
        self.total_bookings = bookings.count()
        self.total_revenue = sum(booking.total_amount for booking in bookings)
        
        # Calculate average rating
        reviews = self.resort.reviews.all()
        if reviews.exists():
            self.average_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
        
        # Calculate occupancy rate
        total_rooms = self.resort.room_count
        occupied_rooms = bookings.filter(status='confirmed').count()
        self.occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0
        
        self.save()

    def get_peak_seasons(self):
        bookings_by_month = {}
        for booking in self.resort.bookings.all():
            month = booking.check_in.month
            bookings_by_month[month] = bookings_by_month.get(month, 0) + 1
        return sorted(bookings_by_month.items(), key=lambda x: x[1], reverse=True)[:3]

    def get_revenue_trends(self):
        monthly_revenue = {}
        for booking in self.resort.bookings.all():
            month = booking.created_at.strftime('%Y-%m')
            monthly_revenue[month] = monthly_revenue.get(month, 0) + booking.total_amount
        return monthly_revenue

class DynamicPricing(models.Model):
    resort = models.OneToOneField(Resort, on_delete=models.CASCADE, related_name='pricing')
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    weekend_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.2)
    peak_season_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.5)
    last_minute_discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.8)
    advance_booking_discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.9)
    minimum_price = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_history = models.JSONField(default=list)
    last_updated = models.DateTimeField(auto_now=True)

    def calculate_dynamic_price(self, check_in_date, check_out_date):
        base = float(self.base_price)
        price_adjustments = []

        # Weekend pricing
        if check_in_date.weekday() >= 5:  # Saturday or Sunday
            base *= float(self.weekend_multiplier)
            price_adjustments.append(('Weekend Rate', f'{float(self.weekend_multiplier)}x'))

        # Peak season pricing
        peak_seasons = self.resort.analytics.peak_season_months
        if check_in_date.month in peak_seasons:
            base *= float(self.peak_season_multiplier)
            price_adjustments.append(('Peak Season', f'{float(self.peak_season_multiplier)}x'))

        # Last minute booking (within 3 days)
        days_until_checkin = (check_in_date - now().date()).days
        if days_until_checkin <= 3:
            base *= float(self.last_minute_discount)
            price_adjustments.append(('Last Minute', f'{float(self.last_minute_discount)}x'))
        # Advance booking discount (more than 30 days)
        elif days_until_checkin > 30:
            base *= float(self.advance_booking_discount)
            price_adjustments.append(('Advance Booking', f'{float(self.advance_booking_discount)}x'))

        # Ensure price is within bounds
        final_price = max(float(self.minimum_price), min(base, float(self.maximum_price)))

        return {
            'final_price': final_price,
            'adjustments': price_adjustments,
            'original_price': float(self.base_price)
        }

    def update_price_history(self, price_data):
        history = self.price_history
        history.append({
            'date': now().isoformat(),
            'price': price_data['final_price'],
            'adjustments': price_data['adjustments']
        })
        self.price_history = history[-30:]  # Keep last 30 days
        self.save()

class BookingAnalytics(models.Model):
    resort = models.OneToOneField(Resort, on_delete=models.CASCADE, related_name='booking_analytics')
    booking_patterns = models.JSONField(default=dict)
    cancellation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_stay_duration = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    repeat_customer_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    popular_add_ons = models.JSONField(default=list)
    seasonal_demand = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    def update_booking_patterns(self):
        bookings = self.resort.bookings.all()
        patterns = {
            'weekday_distribution': {},
            'booking_lead_time': {},
            'length_of_stay': {},
            'party_size': {}
        }
        
        for booking in bookings:
            # Weekday distribution
            weekday = booking.check_in.strftime('%A')
            patterns['weekday_distribution'][weekday] = patterns['weekday_distribution'].get(weekday, 0) + 1
            
            # Booking lead time
            lead_time = (booking.check_in - booking.created_at.date()).days
            lead_bucket = f"{(lead_time // 7) * 7}-{(lead_time // 7 + 1) * 7} days"
            patterns['booking_lead_time'][lead_bucket] = patterns['booking_lead_time'].get(lead_bucket, 0) + 1
            
            # Length of stay
            stay_length = (booking.check_out - booking.check_in).days
            stay_bucket = f"{stay_length} days"
            patterns['length_of_stay'][stay_bucket] = patterns['length_of_stay'].get(stay_bucket, 0) + 1
            
            # Party size
            party_bucket = f"{booking.guests} guests"
            patterns['party_size'][party_bucket] = patterns['party_size'].get(party_bucket, 0) + 1
        
        self.booking_patterns = patterns
        self.save()

    def calculate_metrics(self):
        bookings = self.resort.bookings.all()
        total_bookings = bookings.count()
        
        if total_bookings > 0:
            # Cancellation rate
            cancelled = bookings.filter(status='cancelled').count()
            self.cancellation_rate = (cancelled / total_bookings) * 100
            
            # Average stay duration
            total_days = sum((b.check_out - b.check_in).days for b in bookings)
            self.average_stay_duration = total_days / total_bookings
            
            # Repeat customer rate
            unique_customers = len(set(booking.guest for booking in bookings))
            self.repeat_customer_rate = ((total_bookings - unique_customers) / total_bookings) * 100
        
        self.save()

class RevenueAnalytics(models.Model):
    resort = models.OneToOneField(Resort, on_delete=models.CASCADE, related_name='revenue_analytics')
    daily_revenue = models.JSONField(default=dict)
    monthly_revenue = models.JSONField(default=dict)
    revenue_by_room_type = models.JSONField(default=dict)
    revenue_by_package = models.JSONField(default=dict)
    average_daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    revpar = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Revenue per available room
    goppar = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Gross operating profit per available room
    last_updated = models.DateTimeField(auto_now=True)

    def calculate_metrics(self):
        bookings = self.resort.bookings.all()
        total_rooms = self.resort.room_count
        
        # Calculate RevPAR
        if total_rooms > 0:
            total_revenue = sum(booking.total_amount for booking in bookings)
            self.revpar = total_revenue / (total_rooms * 30)  # 30 days period
        
        # Calculate ADR (Average Daily Rate)
        occupied_room_nights = sum((b.check_out - b.check_in).days for b in bookings)
        if occupied_room_nights > 0:
            self.average_daily_rate = total_revenue / occupied_room_nights
        
        self.save()

    def update_revenue_distribution(self):
        bookings = self.resort.bookings.all()
        
        # Revenue by room type
        room_type_revenue = {}
        for booking in bookings:
            room_type = booking.room_type
            room_type_revenue[room_type] = room_type_revenue.get(room_type, 0) + booking.total_amount
        
        self.revenue_by_room_type = room_type_revenue
        
        # Revenue by package
        package_revenue = {}
        for booking in bookings:
            package = booking.package_type
            if package:
                package_revenue[package] = package_revenue.get(package, 0) + booking.total_amount
        
        self.revenue_by_package = package_revenue
        self.save()

class Package(models.Model):
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name="packages")
    package_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in hours for daycation or days for staycation")
    package_type = models.CharField(max_length=20, choices=[('Staycation', 'Staycation'), ('Daycation', 'Daycation')])
    amenities = models.TextField(help_text="Comma-separated amenities")
    image = models.ImageField(upload_to="package_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    max_guests = models.PositiveIntegerField(default=2)
    availability = models.PositiveIntegerField(default=10, help_text="Number of packages available")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Discount percentage")
    featured = models.BooleanField(default=False)
    total_bookings = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'

    def __str__(self):
        return f"{self.package_name} - {self.resort.resort_name}"

    def get_discounted_price(self):
        if self.discount_percentage > 0:
            discount = (self.price * self.discount_percentage) / 100
            return self.price - discount
        return self.price

    def get_duration_display(self):
        if self.package_type == 'Staycation':
            return f"{self.duration} days"
        return f"{self.duration} hours"

    def get_amenities_list(self):
        return [amenity.strip() for amenity in self.amenities.split(',') if amenity.strip()]

    def is_available(self):
        return self.is_active and self.availability > 0

    def update_stats(self, new_rating=None):
        from django.db.models import Avg
        # Update total bookings
        self.total_bookings = self.bookings.count()
        
        # Update average rating if ratings exist
        if new_rating:
            ratings = list(self.ratings.values_list('rating', flat=True))
            ratings.append(new_rating)
            self.average_rating = sum(ratings) / len(ratings)
        elif self.ratings.exists():
            self.average_rating = self.ratings.aggregate(Avg('rating'))['rating__avg']
        
        self.save()

    def save(self, *args, **kwargs):
        # Validate price and duration
        if self.price < 0:
            raise ValidationError("Price cannot be negative")
        if self.duration <= 0:
            raise ValidationError("Duration must be greater than zero")
        
        # Clean amenities
        if self.amenities:
            amenities_list = [item.strip() for item in self.amenities.split(',') if item.strip()]
            self.amenities = ', '.join(amenities_list)
        
        super().save(*args, **kwargs)

class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
        ('villa', 'Villa'),
    ]

    ROOM_STATUS = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved'),
        ('cleaning', 'Being Cleaned'),
    ]

    resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    floor = models.PositiveIntegerField(default=1)
    capacity = models.PositiveIntegerField(default=2)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_status = models.CharField(max_length=20, choices=ROOM_STATUS, default='available')
    is_active = models.BooleanField(default=True)
    amenities = models.TextField(help_text="List of amenities, separated by commas")
    description = models.TextField(blank=True, null=True)
    size_sqft = models.PositiveIntegerField(null=True, blank=True)
    view_type = models.CharField(max_length=50, blank=True, null=True)
    bed_type = models.CharField(max_length=50, blank=True, null=True)
    last_cleaned = models.DateTimeField(null=True, blank=True)
    next_maintenance = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to='room_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['room_number']
        unique_together = ['resort', 'room_number']

    def __str__(self):
        return f"Room {self.room_number} - {self.get_room_type_display()} at {self.resort.resort_name}"

    def get_amenities_list(self):
        return [amenity.strip() for amenity in self.amenities.split(',') if amenity.strip()]

    def get_current_price(self):
        """Calculate current price based on various factors"""
        price = self.base_price
        
        # Apply weekend pricing
        if timezone.now().weekday() >= 5:  # Saturday or Sunday
            price *= Decimal('1.2')
        
        # Apply seasonal pricing
        if self.is_peak_season():
            price *= Decimal('1.5')
        
        # Apply last-minute discount
        if self.has_last_minute_availability():
            price *= Decimal('0.8')
        
        return price

    def is_peak_season(self):
        """Check if current date falls in peak season"""
        current_month = timezone.now().month
        # Example: Peak season is June through August
        return 6 <= current_month <= 8

    def has_last_minute_availability(self):
        """Check if room has last-minute availability"""
        tomorrow = timezone.now() + timedelta(days=1)
        return self.is_available_on(tomorrow)

    def is_available_on(self, date):
        """Check if room is available on a specific date"""
        return not self.bookings.filter(
            Q(check_in__lte=date, check_out__gt=date) |
            Q(check_in__lt=date + timedelta(days=1), check_out__gt=date)
        ).exists()

    def get_availability_calendar(self, start_date, end_date):
        """Get room availability calendar for a date range"""
        bookings = self.bookings.filter(
            Q(check_in__range=(start_date, end_date)) |
            Q(check_out__range=(start_date, end_date))
        ).order_by('check_in')
        
        calendar = []
        current_date = start_date
        
        while current_date <= end_date:
            is_available = self.is_available_on(current_date)
            calendar.append({
                'date': current_date,
                'available': is_available,
                'price': self.get_current_price() if is_available else None
            })
            current_date += timedelta(days=1)
        
        return calendar

    def get_occupancy_stats(self, days=30):
        """Get occupancy statistics for the last X days"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        total_days = (end_date - start_date).days
        occupied_days = self.bookings.filter(
            check_in__lte=end_date,
            check_out__gt=start_date
        ).count()
        
        return {
            'occupancy_rate': (occupied_days / total_days) * 100 if total_days > 0 else 0,
            'total_days': total_days,
            'occupied_days': occupied_days,
            'revenue': self.get_revenue_for_period(start_date, end_date)
        }

    def get_revenue_for_period(self, start_date, end_date):
        """Calculate revenue for a specific period"""
        bookings = self.bookings.filter(
            check_in__lte=end_date,
            check_out__gt=start_date
        )
        return sum(booking.total_amount for booking in bookings)

    def needs_cleaning(self):
        """Check if room needs cleaning based on last cleaned timestamp"""
        if not self.last_cleaned:
            return True
        hours_since_cleaned = (timezone.now() - self.last_cleaned).total_seconds() / 3600
        return hours_since_cleaned >= 24

    def needs_maintenance(self):
        """Check if room needs maintenance"""
        if not self.next_maintenance:
            return False
        return timezone.now() >= self.next_maintenance

    def mark_as_cleaned(self):
        """Mark room as cleaned"""
        self.last_cleaned = timezone.now()
        self.current_status = 'available'
        self.save()

    def schedule_maintenance(self, maintenance_date):
        """Schedule maintenance for the room"""
        self.next_maintenance = maintenance_date
        self.save()

    def update_status(self, status):
        """Update room status"""
        if status in dict(self.ROOM_STATUS):
            self.current_status = status
            self.save()
        else:
            raise ValueError(f"Invalid status: {status}")

class GuestUser(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email Address")
    full_name = models.CharField(max_length=255, verbose_name="Full Name")
    mobile_number = models.CharField(max_length=15, unique=True, verbose_name="Mobile Number")
    password = models.CharField(max_length=255, verbose_name="Password")
    profile_image = models.ImageField(upload_to='guest_profiles/', null=True, blank=True, verbose_name="Profile Picture")
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Account Status")
    preferences = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Guest User"
        verbose_name_plural = "Guest Users"
        ordering = ['-date_joined']

    def __str__(self):
        return self.full_name

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split()[0]

    def set_password(self, raw_password):
        """Set the user's password using Django's password hashing."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash."""
        return check_password(raw_password, self.password)

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def activate(self):
        """Activate the user account."""
        self.is_active = True
        self.save(update_fields=['is_active'])

    def update_preferences(self, new_preferences):
        """Update user preferences with timestamp."""
        if not isinstance(new_preferences, dict):
            raise ValueError("Preferences must be a dictionary")
        
        current_preferences = self.preferences or {}
        current_preferences.update(new_preferences)
        current_preferences['last_updated'] = timezone.now().isoformat()
        
        self.preferences = current_preferences
        self.save(update_fields=['preferences'])

    def get_profile_image_url(self):
        """Get the profile image URL or return default image URL."""
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return '/static/images/default-profile.png'

    def delete_profile_image(self):
        """Delete the user's profile image if it exists."""
        if self.profile_image:
            if os.path.isfile(self.profile_image.path):
                os.remove(self.profile_image.path)
            self.profile_image = None
            self.save(update_fields=['profile_image'])

    def clean(self):
        """Validate model fields."""
        # Validate mobile number format
        if self.mobile_number:
            if not self.mobile_number.isdigit():
                raise ValidationError({'mobile_number': 'Mobile number must contain only digits'})
            if len(self.mobile_number) < 10:
                raise ValidationError({'mobile_number': 'Mobile number must be at least 10 digits'})
        
        # Validate email format
        if self.email:
            self.email = self.email.lower().strip()

        # Validate preferences format
        if self.preferences and not isinstance(self.preferences, dict):
            raise ValidationError({'preferences': 'Preferences must be a valid JSON object'})

    def save(self, *args, **kwargs):
        """Override save method to perform additional operations."""
        # Capitalize each word in full name
        if self.full_name:
            self.full_name = self.full_name.title().strip()
        
        # Clean and validate fields
        self.clean()
        
        # If this is a new user, set date_joined
        if not self.pk:
            self.date_joined = timezone.now()
        
        super().save(*args, **kwargs)

    @property
    def is_authenticated(self):
        """Check if the user is authenticated."""
        return True if self.is_active else False

    @property
    def get_preferences_list(self):
        """Get user preferences as a list."""
        return self.preferences.get('interests', []) if self.preferences else []

    @property
    def last_login_formatted(self):
        """Get formatted last login time."""
        if self.last_login:
            return self.last_login.strftime("%B %d, %Y at %I:%M %p")
        return "Never"

    @property
    def member_since(self):
        """Get formatted member since date."""
        return self.date_joined.strftime("%B %Y")

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    guest = models.ForeignKey(GuestUser, on_delete=models.CASCADE, related_name='reviews')
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        reviewed_item = self.resort or self.package or self.room
        return f"{self.guest.full_name}'s {self.rating}-star review for {reviewed_item}"

    def clean(self):
        # Ensure only one of resort, package, or room is set
        if sum(bool(x) for x in [self.resort, self.package, self.room]) != 1:
            raise ValidationError("Review must be associated with exactly one of: resort, package, or room")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        # Update average rating for the reviewed item
        if self.resort:
            self.update_resort_rating()
        elif self.package:
            self.update_package_rating()
        elif self.room:
            self.update_room_rating()

    def update_resort_rating(self):
        """Update the resort's average rating"""
        avg_rating = self.resort.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        self.resort.average_rating = round(avg_rating, 2)
        self.resort.total_reviews = self.resort.reviews.count()
        self.resort.save()

    def update_package_rating(self):
        """Update the package's average rating"""
        avg_rating = self.package.reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        self.package.average_rating = round(avg_rating, 2)
        self.package.save()

    def update_room_rating(self):
        """Update the room's rating statistics"""
        # If you have rating fields in the Room model, update them here
        pass

class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ]

    FOOD_PREFERENCE = [
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
        ('both', 'Both')
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded')
    ]

    guest = models.ForeignKey(GuestUser, on_delete=models.CASCADE)
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Booking Details
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    
    # Guest Preferences
    food_preference = models.CharField(max_length=10, choices=FOOD_PREFERENCE, default='both')
    special_requests = models.TextField(blank=True, null=True)
    
    # Payment Information
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.check_in and self.check_out:
            if self.check_in < timezone.now().date():
                raise ValidationError("Check-in date cannot be in the past")
            if self.check_out <= self.check_in:
                raise ValidationError("Check-out date must be after check-in date")
            if self.package and self.room:
                raise ValidationError("Cannot book both package and room. Choose one.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def total_nights(self):
        return (self.check_out - self.check_in).days

    @property
    def balance_amount(self):
        return self.total_amount - self.paid_amount

    def __str__(self):
        return f"Booking #{self.id} - {self.guest.name}"

class BookingPayment(models.Model):
    PAYMENT_METHOD = [
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Digital Wallet')
    ]

    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=200, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id or self.razorpay_order_id} for Booking #{self.booking.id}"

    class Meta:
        ordering = ['-created_at']

class RoomAvailability(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('room', 'date')

    def __str__(self):
        status = "Available" if self.is_available else "Booked"
        return f"{self.room.room_type} - {self.date} - {status}"

class PackageAvailability(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    date = models.DateField()
    total_slots = models.PositiveIntegerField()
    booked_slots = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('package', 'date')

    @property
    def available_slots(self):
        return max(0, self.total_slots - self.booked_slots)

    @property
    def is_available(self):
        return self.available_slots > 0

    def __str__(self):
        return f"{self.package.package_name} - {self.date} ({self.available_slots} slots available)"

class PackageBooking(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='bookings')
    guest_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    check_in = models.DateField()
    guests = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.guest_name}'s booking for {self.package.package_name}"

class UserInterestEnquiry(models.Model):
    INTEREST_CHOICES = [
        ('Relaxation & Wellness', 'Relaxation & Wellness'),
        ('Outdoor Adventure', 'Outdoor Adventure'),
        ('Luxury & Pampering', 'Luxury & Pampering'),
        ('Cultural Exploration', 'Cultural Exploration'),
        ('Eco-Friendly Travel', 'Eco-Friendly Travel')
    ]

    BUDGET_CHOICES = [
        ('2000-5000', '₹2,000 - ₹5,000'),
        ('5000-10000', '₹5,000 - ₹10,000'),
        ('10000-20000', '₹10,000 - ₹20,000'),
        ('20000+', 'Above ₹20,000')
    ]

    DURATION_PREFERENCE = [
        ('day', 'Day Trip (4-8 hours)'),
        ('weekend', 'Weekend (1-2 days)'),
        ('week', 'Week Long (3-7 days)'),
        ('flexible', 'Flexible')
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    interests = models.JSONField(help_text="List of selected interests")
    budget_range = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    preferred_duration = models.CharField(max_length=20, choices=DURATION_PREFERENCE)
    travel_date = models.DateField(null=True, blank=True)
    number_of_people = models.PositiveIntegerField(default=1)
    special_requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    recommendations = models.JSONField(null=True, blank=True, help_text="Stored package recommendations")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Interest Enquiry'
        verbose_name_plural = 'User Interest Enquiries'

    def __str__(self):
        return f"{self.name}'s Enquiry - {self.created_at.strftime('%Y-%m-%d')}"

class PackageRecommendation(models.Model):
    INTEREST_CATEGORIES = [
        ('Relaxation & Wellness', 'Relaxation & Wellness'),
        ('Outdoor Adventure', 'Outdoor Adventure'),
        ('Luxury & Pampering', 'Luxury & Pampering'),
        ('Cultural Exploration', 'Cultural Exploration'),
        ('Eco-Friendly Travel', 'Eco-Friendly Travel')
    ]

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='recommendations')
    interest_category = models.CharField(max_length=50, choices=INTEREST_CATEGORIES)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_featured = models.BooleanField(default=False)
    min_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recommended_duration = models.CharField(
        max_length=20,
        choices=[
            ('day', 'Day Trip (4-8 hours)'),
            ('weekend', 'Weekend (1-2 days)'),
            ('week', 'Week Long (3-7 days)'),
            ('flexible', 'Flexible')
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-confidence_score']
        verbose_name = 'Package Recommendation'
        verbose_name_plural = 'Package Recommendations'

    def __str__(self):
        return f"{self.package.package_name} - {self.interest_category} ({self.confidence_score})"

    @staticmethod
    def get_recommendations_for_interests(interests, budget_range=None, duration=None, limit=3):
        """Get static recommendations based on user interests and preferences."""
        recommendations = PackageRecommendation.objects.filter(
            interest_category__in=interests,
            package__is_active=True
        )

        if budget_range and budget_range != '20000+':
            max_budget = int(budget_range.split('-')[1])
            recommendations = recommendations.filter(package__price__lte=max_budget)

        if duration and duration != 'flexible':
            recommendations = recommendations.filter(recommended_duration=duration)

        return recommendations.order_by('-confidence_score', '-package__average_rating')[:limit]

    def matches_user_preferences(self, budget_range=None, duration=None):
        """Check if the recommendation matches user preferences."""
        if budget_range and budget_range != '20000+':
            max_budget = int(budget_range.split('-')[1])
            if self.package.price > max_budget:
                return False

        if duration and duration != 'flexible':
            if self.recommended_duration != duration:
                return False

        return True

class Membership(models.Model):
    PLAN_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('luxury', 'Luxury'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s {self.plan_type} Membership"
    
    def is_active(self):
        return self.status == 'active' and self.end_date > timezone.now()
    
    def days_remaining(self):
        if not self.is_active():
            return 0
        return (self.end_date - timezone.now()).days
    
    def cancel(self):
        self.status = 'cancelled'
        self.end_date = timezone.now()
        self.save()

