from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, PackageForm
from .models import UserDB, Resort, ResortImage, Package
import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError


# Create your views here.
def index(request):
    return render(request, 'index.html')

def resortindex(request):
    return render(request, 'Resortindex.html')

def guestindex(request):
    return render(request, 'guestindex.html')

def about(request):
    return render(request, 'about.html')

def blog(request):
    return render(request, 'blog.html')

def blog_single(request, slug):
    # You can use the slug to fetch the specific blog post
    context = {
        'slug': slug
    }
    return render(request, 'blog-single.html', context)

def contact(request):
    return render(request, 'contact.html')

def main(request):
    return render(request, 'main.html')

def restaurants(request):
    return render(request, 'restaurants.html')

def rooms(request):
    return render(request, 'rooms.html')

def rooms_single(request, room_id):
    # You can add logic here to fetch room details based on room_id
    context = {
        'room_id': room_id,
        # Add other room details as needed
    }
    return render(request, 'rooms-single.html', context)

def ResortDashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to access the dashboard.')
        return redirect('user_login')

    try:
        resort = Resort.objects.get(user=request.user)
        
        # Get package statistics
        packages = resort.packages.all()
        staycation_packages = packages.filter(package_type='Staycation')
        daycation_packages = packages.filter(package_type='Daycation')
        
        # Get popular packages
        popular_packages = packages.order_by('-total_bookings')[:5]
        
        context = {
            'resort': resort,
            'statistics': {
                'occupancy_rate': resort.get_occupancy_rate(),
                'monthly_revenue': resort.get_monthly_revenue(),
                'total_guests': resort.get_total_guests(),
                'average_rating': resort.get_average_rating(),
            },
            'recent_bookings': resort.get_recent_bookings(),
            'monthly_stats': resort.get_monthly_stats(),
            'resort_images': resort.images.all()[:6],
            'facilities': resort.get_facility_groups(),
            'today_date': datetime.now().strftime('%B %d, %Y'),
            
            # Package statistics
            'package_stats': {
                'total_packages': packages.count(),
                'staycation_count': staycation_packages.count(),
                'daycation_count': daycation_packages.count(),
                'active_packages': packages.filter(is_active=True).count(),
            },
            'popular_packages': [
                {
                    'name': pkg.package_name,
                    'type': pkg.package_type,
                    'price': pkg.get_discounted_price(),
                    'total_bookings': pkg.total_bookings,
                    'rating': pkg.average_rating,
                    'availability': pkg.availability,
                    'image': pkg.image.url if pkg.image else None,
                }
                for pkg in popular_packages
            ],
            'featured_packages': packages.filter(featured=True)[:3],
            'recent_packages': packages.order_by('-created_at')[:5],
            
            # Revenue data for charts
            'revenue_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'revenue_data': resort.revenue_analytics.monthly_revenue if hasattr(resort, 'revenue_analytics') else [],
            'occupancy_data': [75, 82, 85, 88, 90, 95],  # Example data
            
            # Package type distribution for charts
            'package_distribution': {
                'labels': ['Staycation', 'Daycation'],
                'data': [staycation_packages.count(), daycation_packages.count()]
            },
        }
        return render(request, 'ResortDashboard.html', context)
    
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

def generate_verification_code():
    return get_random_string(length=6, allowed_chars='0123456789')

def user_signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, "Registration successful! You can now login.")
                return redirect('user_login')
            except Exception as e:
                messages.error(request, f"An error occurred during registration: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, "signup.html", {"form": form})

def verify_email(request, user_id):
    try:
        user = UserDB.objects.get(id=user_id)
        if user.is_active:
            messages.warning(request, "Your email is already verified.")
            return redirect('user_login')

        if request.method == "POST":
            submitted_code = request.POST.get('verification_code')
            stored_code = cache.get(f'verification_code_{user_id}')

            if not stored_code:
                messages.error(request, "Verification code has expired. Please request a new one.")
                return render(request, 'verify_email.html', {'user': user})

            if submitted_code == stored_code:
                user.is_active = True
                user.is_verified = True
                user.save()
                cache.delete(f'verification_code_{user_id}')
                messages.success(request, "Email verified successfully! You can now log in.")
                return redirect('user_login')
            else:
                messages.error(request, "Invalid verification code. Please try again.")

        # Get stored code for display
        verification_code = cache.get(f'verification_code_{user_id}')
        return render(request, 'verify_email.html', {
            'user': user,
            'verification_code': verification_code
        })

    except UserDB.DoesNotExist:
        messages.error(request, "Invalid user account.")
        return redirect('user_signup')

def resend_verification(request, user_id):
    try:
        user = UserDB.objects.get(id=user_id)
        if user.is_active:
            messages.warning(request, "Your email is already verified.")
            return redirect('user_login')

        # Generate new verification code
        verification_code = generate_verification_code()
        cache.set(f'verification_code_{user.id}', verification_code, timeout=3600)

        # Resend verification email
        send_mail(
            subject="New Verification Code - LuxAI Resorts",
            message=f"""Hello {user.name},

Your new verification code is: {verification_code}

Please use this code to verify your email address. The code will expire in 1 hour.

Best regards,
LuxAI Resorts Team""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        messages.success(request, "New verification code has been sent to your email.")
        return redirect('verify_email', user_id=user.id)

    except UserDB.DoesNotExist:
        messages.error(request, "Invalid user account.")
        return redirect('user_signup')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        # Try to authenticate with username first
        user = authenticate(request, username=username, password=password)
        
        # If authentication fails, try with email
        if user is None:
            try:
                user_obj = UserDB.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except UserDB.DoesNotExist:
                user = None
        
        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account is not active. Please verify your email first.')
                return render(request, 'login.html')
                
            login(request, user)
            
            # Set session expiry based on remember me choice
            if remember_me:
                # Set session to expire in 2 weeks
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)  # Session expires when browser closes
                
            messages.success(request, 'Login successful!')
            
            # Redirect based on user type
            if user.designation == 'owner' or user.designation == 'manager':
                return redirect('resortindex')
            else:
                return redirect('guestindex')
        else:
            messages.error(request, 'Invalid username/email or password.')
            
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('index')

@login_required
def profile(request):
    user = request.user
    resort = None
    context = {
        'user': user,
        'total_bookings': 0,  # Will be updated when booking model is implemented
        'active_packages': 0,
        'average_rating': 0,
    }
    
    if hasattr(user, 'resort'):
        resort = user.resort
        context.update({
            'resort': resort,
            
            # Basic Facilities
            'basic_facilities': [
                {'name': 'Swimming Pool', 'available': resort.has_pool},
                {'name': 'Spa & Wellness', 'available': resort.has_spa},
                {'name': 'Restaurant', 'available': resort.has_restaurant},
                {'name': 'Fitness Center', 'available': resort.has_gym},
                {'name': 'High-Speed Wi-Fi', 'available': resort.has_wifi},
                {'name': 'Valet Parking', 'available': resort.has_parking},
            ],
            
            # Staycation Packages
            'staycation_packages': [
                {'name': 'Romantic Getaway', 'available': resort.has_romantic_package},
                {'name': 'Family Vacation', 'available': resort.has_family_package},
                {'name': 'Business Stay', 'available': resort.has_business_package},
                {'name': 'Wellness Retreat', 'available': resort.has_wellness_package},
                {'name': 'Extended Stay', 'available': resort.has_longstay_package},
                {'name': 'Work From Resort', 'available': resort.has_workation_package},
            ],
            
            # Daycation Packages
            'daycation_packages': [
                {'name': 'Pool Day Pass', 'available': resort.has_pool_access},
                {'name': 'Spa Day Package', 'available': resort.has_spa_day},
                {'name': 'Dining Experience', 'available': resort.has_dining},
                {'name': 'Day Workspace', 'available': resort.has_workspace},
            ],
            
            # Venue Functions
            'venue_functions': [
                {'name': 'Wedding Venue', 'available': resort.has_wedding_venue},
                {'name': 'Conference Hall', 'available': resort.has_conference_hall},
                {'name': 'Banquet Hall', 'available': resort.has_banquet_hall},
                {'name': 'Outdoor Events', 'available': resort.has_outdoor_venue},
            ],
            
            # Activities
            'activities': [
                {'name': 'Water Sports', 'available': resort.has_water_sports},
                {'name': 'Trekking Tours', 'available': resort.has_trekking},
                {'name': 'Cycling', 'available': resort.has_cycling},
                {'name': 'Yoga Classes', 'available': resort.has_yoga},
                {'name': 'Cooking Classes', 'available': resort.has_cooking_class},
                {'name': 'Kids Club', 'available': resort.has_kids_club},
            ],
            
            # Transportation
            'transportation': [
                {'name': 'Airport Transfer', 'available': resort.has_airport_transfer},
                {'name': 'Car Rental', 'available': resort.has_car_rental},
                {'name': 'Shuttle Service', 'available': resort.has_shuttle},
                {'name': 'Taxi Booking', 'available': resort.has_taxi},
            ],
            
            # Special Packages
            'special_packages': [
                {'name': 'Student Groups', 'available': resort.has_student_package},
                {'name': 'Senior Citizens', 'available': resort.has_senior_package},
                {'name': 'Corporate Groups', 'available': resort.has_corporate_package},
                {'name': 'Honeymoon', 'available': resort.has_honeymoon_package},
            ],
            
            # Additional Services
            'additional_services': [
                {'name': 'Laundry Service', 'available': resort.has_laundry},
                {'name': 'Childcare', 'available': resort.has_childcare},
                {'name': '24/7 Room Service', 'available': resort.has_room_service},
                {'name': 'Concierge', 'available': resort.has_concierge},
                {'name': 'Medical Assistance', 'available': resort.has_medical},
                {'name': 'Pet Friendly', 'available': resort.is_pet_friendly},
            ],
            
            # Resort Images
            'resort_images': resort.images.all().order_by('-is_primary', '-uploaded_at')[:6],
        })
        
        # Count active packages
        context['active_packages'] = sum(1 for pkg in context['staycation_packages'] + context['daycation_packages'] if pkg['available'])
    
    return render(request, 'profile.html', context)

@login_required
def settings_view(request):
    return render(request, 'settings.html', {
        'user': request.user
    })

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = UserDB.objects.get(email=email)
            # Generate token
            token = get_random_string(64)
            # Store token in cache with expiry
            cache.set(f'password_reset_{token}', user.id, timeout=3600)  # 1 hour expiry
            
            # Generate reset link
            reset_link = request.build_absolute_uri(
                reverse('reset_password') + f'?token={token}'
            )
            
            email_subject = 'Reset Your Password - LuxAI Resorts'
            email_body = f'''Hello {user.name},

You have requested to reset your password. Please click the link below to set a new password:

{reset_link}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
LuxAI Resorts Team'''

            try:
                # Send email
                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('user_login')
            
            except Exception as e:
                # Delete the token from cache if email fails
                cache.delete(f'password_reset_{token}')
                print(f"Email Error: {str(e)}")  # For debugging
                messages.error(request, 'Failed to send password reset email. Please try again later.')
                if settings.DEBUG:
                    messages.error(request, f'Error details: {str(e)}')
                return render(request, 'forgot_password.html')
                
        except UserDB.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    
    return render(request, 'forgot_password.html')

def reset_password(request):
    token = request.GET.get('token')
    if not token:
        messages.error(request, 'Invalid password reset link.')
        return redirect('user_login')
    
    user_id = cache.get(f'password_reset_{token}')
    if not user_id:
        messages.error(request, 'Password reset link has expired or is invalid.')
        return redirect('user_login')
    
    try:
        user = UserDB.objects.get(id=user_id)
    except UserDB.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('user_login')
    
    if request.method == 'POST':
        password1 = request.POST.get('new_password1')
        password2 = request.POST.get('new_password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'reset_password.html', {'token': token})
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'reset_password.html', {'token': token})
        
        # Update password
        user.set_password(password1)
        user.save()
        
        # Delete token from cache
        cache.delete(f'password_reset_{token}')
        
        messages.success(request, 'Password has been reset successfully. You can now login with your new password.')
        return redirect('user_login')
    
    return render(request, 'reset_password.html', {'token': token})

@login_required
def edit_resort(request):
    try:
        resort = Resort.objects.get(user=request.user)
        if request.method == 'POST':
            # Handle form submission
            resort.resort_name = request.POST.get('resort_name', resort.resort_name)
            resort.resort_address = request.POST.get('resort_address', resort.resort_address)
            resort.resort_contact = request.POST.get('resort_contact', resort.resort_contact)
            resort.resort_email = request.POST.get('resort_email', resort.resort_email)
            resort.resort_website = request.POST.get('resort_website', resort.resort_website)
            resort.resort_description = request.POST.get('resort_description', resort.resort_description)
            resort.resort_type = request.POST.get('resort_type', resort.resort_type)
            resort.room_count = request.POST.get('room_count', resort.room_count)
            
            # Basic Facilities
            resort.has_pool = request.POST.get('has_pool') == 'on'
            resort.has_spa = request.POST.get('has_spa') == 'on'
            resort.has_restaurant = request.POST.get('has_restaurant') == 'on'
            resort.has_gym = request.POST.get('has_gym') == 'on'
            resort.has_wifi = request.POST.get('has_wifi') == 'on'
            resort.has_parking = request.POST.get('has_parking') == 'on'
            
            # Save changes
            resort.save()
            messages.success(request, 'Resort details updated successfully!')
            return redirect('view_profile')
            
        return render(request, 'edit_resort.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.error(request, 'Resort not found.')
        return redirect('view_profile')

@login_required
def manage_facilities(request):
    try:
        resort = Resort.objects.get(user=request.user)
        if request.method == 'POST':
            # Update boolean fields
            resort.has_pool = request.POST.get('has_pool') == 'on'
            resort.has_spa = request.POST.get('has_spa') == 'on'
            resort.has_restaurant = request.POST.get('has_restaurant') == 'on'
            resort.has_gym = request.POST.get('has_gym') == 'on'
            resort.has_wifi = request.POST.get('has_wifi') == 'on'
            resort.has_parking = request.POST.get('has_parking') == 'on'

            resort.has_wedding_venue = request.POST.get('has_wedding_venue') == 'on'
            resort.has_conference_hall = request.POST.get('has_conference_hall') == 'on'
            resort.has_banquet_hall = request.POST.get('has_banquet_hall') == 'on'
            resort.has_outdoor_venue = request.POST.get('has_outdoor_venue') == 'on'

            resort.has_water_sports = request.POST.get('has_water_sports') == 'on'
            resort.has_trekking = request.POST.get('has_trekking') == 'on'
            resort.has_cycling = request.POST.get('has_cycling') == 'on'
            resort.has_yoga = request.POST.get('has_yoga') == 'on'
            resort.has_cooking_class = request.POST.get('has_cooking_class') == 'on'
            resort.has_kids_club = request.POST.get('has_kids_club') == 'on'

            resort.has_airport_transfer = request.POST.get('has_airport_transfer') == 'on'
            resort.has_car_rental = request.POST.get('has_car_rental') == 'on'
            resort.has_shuttle = request.POST.get('has_shuttle') == 'on'
            resort.has_taxi = request.POST.get('has_taxi') == 'on'

            resort.has_laundry = request.POST.get('has_laundry') == 'on'
            resort.has_childcare = request.POST.get('has_childcare') == 'on'
            resort.has_room_service = request.POST.get('has_room_service') == 'on'
            resort.has_concierge = request.POST.get('has_concierge') == 'on'
            resort.has_medical = request.POST.get('has_medical') == 'on'
            resort.is_pet_friendly = request.POST.get('is_pet_friendly') == 'on'

            resort.save()
            messages.success(request, 'Facilities updated successfully!')
            return redirect('view_profile')

        context = {
            'resort': resort,
            'basic_facilities': [
                {'name': 'Swimming Pool', 'field': 'has_pool', 'value': resort.has_pool},
                {'name': 'Spa & Wellness', 'field': 'has_spa', 'value': resort.has_spa},
                {'name': 'Restaurant', 'field': 'has_restaurant', 'value': resort.has_restaurant},
                {'name': 'Fitness Center', 'field': 'has_gym', 'value': resort.has_gym},
                {'name': 'High-Speed Wi-Fi', 'field': 'has_wifi', 'value': resort.has_wifi},
                {'name': 'Valet Parking', 'field': 'has_parking', 'value': resort.has_parking},
            ],
            'venue_functions': [
                {'name': 'Wedding Venue', 'field': 'has_wedding_venue', 'value': resort.has_wedding_venue},
                {'name': 'Conference Hall', 'field': 'has_conference_hall', 'value': resort.has_conference_hall},
                {'name': 'Banquet Hall', 'field': 'has_banquet_hall', 'value': resort.has_banquet_hall},
                {'name': 'Outdoor Events', 'field': 'has_outdoor_venue', 'value': resort.has_outdoor_venue},
            ],
            'activities': [
                {'name': 'Water Sports', 'field': 'has_water_sports', 'value': resort.has_water_sports},
                {'name': 'Trekking Tours', 'field': 'has_trekking', 'value': resort.has_trekking},
                {'name': 'Cycling', 'field': 'has_cycling', 'value': resort.has_cycling},
                {'name': 'Yoga Classes', 'field': 'has_yoga', 'value': resort.has_yoga},
                {'name': 'Cooking Classes', 'field': 'has_cooking_class', 'value': resort.has_cooking_class},
                {'name': 'Kids Club', 'field': 'has_kids_club', 'value': resort.has_kids_club},
            ],
            'transportation': [
                {'name': 'Airport Transfer', 'field': 'has_airport_transfer', 'value': resort.has_airport_transfer},
                {'name': 'Car Rental', 'field': 'has_car_rental', 'value': resort.has_car_rental},
                {'name': 'Shuttle Service', 'field': 'has_shuttle', 'value': resort.has_shuttle},
                {'name': 'Taxi Booking', 'field': 'has_taxi', 'value': resort.has_taxi},
            ],
            'additional_services': [
                {'name': 'Laundry Service', 'field': 'has_laundry', 'value': resort.has_laundry},
                {'name': 'Childcare', 'field': 'has_childcare', 'value': resort.has_childcare},
                {'name': '24/7 Room Service', 'field': 'has_room_service', 'value': resort.has_room_service},
                {'name': 'Concierge', 'field': 'has_concierge', 'value': resort.has_concierge},
                {'name': 'Medical Assistance', 'field': 'has_medical', 'value': resort.has_medical},
                {'name': 'Pet Friendly', 'field': 'is_pet_friendly', 'value': resort.is_pet_friendly},
            ],
        }
        return render(request, 'manage_facilities.html', context)
    except Resort.DoesNotExist:
        messages.error(request, 'Resort not found.')
        return redirect('view_profile')

@login_required
def view_profile(request):
    try:
        resort = Resort.objects.get(user=request.user)
        resort_images = resort.images.all()
        context = {
            'resort': resort,
            'resort_images': resort_images,
            'is_profile_complete': True
        }
    except Resort.DoesNotExist:
        context = {
            'is_profile_complete': False
        }
    return render(request, 'view_profile.html', context)

@login_required
def edit_profile(request):
    try:
        resort = get_object_or_404(Resort, user=request.user)
        resort_images = resort.images.all()

        if request.method == 'POST':
            try:
                # Basic details
                resort.resort_name = request.POST.get('resort_name')
                resort.resort_type = request.POST.get('resort_type')
                resort.resort_contact = request.POST.get('resort_contact')
                resort.resort_email = request.POST.get('resort_email')
                resort.resort_website = request.POST.get('resort_website')
                resort.resort_address = request.POST.get('resort_address')
                resort.resort_description = request.POST.get('resort_description')
                resort.room_count = request.POST.get('room_count')

                # Handle check-in & check-out time
                check_in_time = request.POST.get('check_in_time')
                check_out_time = request.POST.get('check_out_time')

                if check_in_time and check_out_time:
                    check_in = datetime.strptime(check_in_time, '%H:%M').time()
                    check_out = datetime.strptime(check_out_time, '%H:%M').time()

                    if check_out <= check_in:
                        messages.error(request, 'Check-out time must be after check-in time')
                        return render(request, 'edit_profile.html', {'resort': resort, 'resort_images': resort_images})

                    resort.check_in_time = check_in
                    resort.check_out_time = check_out

                # Update boolean fields
                boolean_fields = [
                    'has_pool', 'has_spa', 'has_restaurant', 'has_gym', 'has_wifi', 'has_parking',
                    'has_romantic_package', 'has_family_package', 'has_business_package',
                    'has_wellness_package', 'has_longstay_package', 'has_workation_package',
                    'has_water_sports', 'has_trekking', 'has_cycling', 'has_yoga',
                    'has_cooking_class', 'has_kids_club', 'has_airport_transfer', 'has_car_rental',
                    'has_shuttle', 'has_taxi', 'has_student_package', 'has_senior_package',
                    'has_corporate_package', 'has_honeymoon_package', 'has_laundry', 'has_childcare',
                    'has_room_service', 'has_concierge', 'has_medical', 'is_pet_friendly'
                ]

                for field in boolean_fields:
                    setattr(resort, field, request.POST.get(field) == 'on')

                # Validate and save resort
                resort.full_clean()
                resort.save()

                # Handle image uploads
                success_count = 0
                error_count = 0
                resort_images = request.FILES.getlist('resort_images')
                
                for image in resort_images:
                    try:
                        # Validate file size (max 5MB)
                        if image.size > 5 * 1024 * 1024:
                            error_count += 1
                            messages.warning(request, f'Image "{image.name}" exceeds 5MB size limit')
                            continue
                            
                        # Validate file type
                        if not image.content_type.startswith('image/'):
                            error_count += 1
                            messages.warning(request, f'File "{image.name}" is not a valid image')
                            continue
                            
                        ResortImage.objects.create(
                            resort=resort,
                            image=image,
                            is_primary=not resort.images.exists()  # First image is primary if no images exist
                        )
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        messages.warning(request, f'Failed to upload image "{image.name}": {str(e)}')

                # Success message with image upload status
                success_msg = 'Resort profile updated successfully!'
                if success_count > 0:
                    success_msg += f' {success_count} image(s) uploaded.'
                if error_count > 0:
                    success_msg += f' {error_count} image(s) failed to upload.'
                messages.success(request, success_msg)
                
                return redirect('view_profile')

            except ValidationError as e:
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
                else:
                    messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {str(e)}')

        return render(request, 'edit_profile.html', {
            'resort': resort,
            'resort_images': resort_images
        })

    except Resort.DoesNotExist:
        messages.error(request, 'Resort profile not found.')
        return redirect('view_profile')

@login_required
def add_profile(request):
    if hasattr(request.user, 'resort'):
        messages.info(request, 'You already have a resort profile. You can edit your existing profile.')
        return redirect('edit_profile')

    if request.method == 'POST':
        try:
            # Validate required fields with descriptive messages
            required_fields = {
                'resort_name': 'Resort Name',
                'resort_type': 'Resort Type',
                'resort_contact': 'Contact Number',
                'resort_address': 'Resort Address',
                'room_count': 'Total Rooms'
            }

            # Check for missing required fields
            missing_fields = []
            form_data = {}
            for field, label in required_fields.items():
                value = request.POST.get(field, '').strip()
                if not value:
                    missing_fields.append(label)
                form_data[field] = value
            
            if missing_fields:
                raise ValidationError(f"Please fill in the following required fields: {', '.join(missing_fields)}")

            # Create resort instance
            resort = Resort(user=request.user)
            
            # Set basic fields
            resort.resort_name = form_data['resort_name']
            resort.resort_type = form_data['resort_type']
            resort.resort_contact = form_data['resort_contact']
            resort.resort_email = request.POST.get('resort_email', '').strip()
            resort.resort_website = request.POST.get('resort_website', '').strip()
            resort.resort_address = form_data['resort_address']
            resort.resort_description = request.POST.get('resort_description', '').strip()
            
            # Validate and set room count
            try:
                room_count = int(form_data['room_count'])
                if room_count <= 0:
                    raise ValueError()
                resort.room_count = room_count
            except (ValueError, TypeError):
                raise ValidationError("Room count must be a positive number")

            # Handle check-in and check-out times
            check_in_time = request.POST.get('check_in_time')
            check_out_time = request.POST.get('check_out_time')
            
            if check_in_time or check_out_time:
                try:
                    if check_in_time:
                        check_in = datetime.strptime(check_in_time, '%H:%M').time()
                        resort.check_in_time = check_in
                    
                    if check_out_time:
                        check_out = datetime.strptime(check_out_time, '%H:%M').time()
                        resort.check_out_time = check_out
                    
                    if check_in_time and check_out_time and check_out <= check_in:
                        raise ValidationError("Check-out time must be after check-in time")
                        
                except ValueError:
                    raise ValidationError("Invalid time format. Please use HH:MM format (e.g., 14:00)")

            # Update boolean fields
            boolean_fields = [
                'has_pool', 'has_spa', 'has_restaurant', 'has_gym', 'has_wifi', 'has_parking',
                'has_romantic_package', 'has_family_package', 'has_business_package',
                'has_wellness_package', 'has_longstay_package', 'has_workation_package',
                'has_pool_access', 'has_spa_day', 'has_dining', 'has_workspace',
                'has_wedding_venue', 'has_conference_hall', 'has_banquet_hall', 'has_outdoor_venue',
                'has_water_sports', 'has_trekking', 'has_cycling', 'has_yoga',
                'has_cooking_class', 'has_kids_club', 'has_airport_transfer', 'has_car_rental',
                'has_shuttle', 'has_taxi', 'has_student_package', 'has_senior_package',
                'has_corporate_package', 'has_honeymoon_package', 'has_laundry', 'has_childcare',
                'has_room_service', 'has_concierge', 'has_medical', 'is_pet_friendly'
            ]
            
            for field in boolean_fields:
                setattr(resort, field, request.POST.get(field) == 'on')

            # Validate and save resort
            resort.full_clean()
            resort.save()

            # Handle image uploads
            success_count = 0
            error_count = 0
            resort_images = request.FILES.getlist('resort_images')
            
            for index, image in enumerate(resort_images):
                try:
                    # Validate file size (max 5MB)
                    if image.size > 5 * 1024 * 1024:
                        error_count += 1
                        messages.warning(request, f'Image "{image.name}" exceeds 5MB size limit')
                        continue
                        
                    # Validate file type
                    if not image.content_type.startswith('image/'):
                        error_count += 1
                        messages.warning(request, f'File "{image.name}" is not a valid image')
                        continue
                        
                    ResortImage.objects.create(
                        resort=resort,
                        image=image,
                        is_primary=(index == 0)  # First image is primary
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    messages.warning(request, f'Failed to upload image "{image.name}": {str(e)}')

            # Success message with image upload status
            success_msg = 'Resort profile created successfully!'
            if success_count > 0:
                success_msg += f' {success_count} image(s) uploaded.'
            if error_count > 0:
                success_msg += f' {error_count} image(s) failed to upload.'
            messages.success(request, success_msg)
            
            return redirect('view_profile')
            
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            else:
                messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')

    return render(request, 'addprofile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('view_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})

@login_required
def manage_bookings(request):
    try:
        resort = Resort.objects.get(user=request.user)
        # Add booking management logic here
        return render(request, 'dashboard/bookings.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def resort_analytics(request):
    try:
        resort = Resort.objects.get(user=request.user)
        context = {
            'resort': resort,
            'analytics': {
                'revenue_data': [30000, 35000, 40000, 38000, 42000, 45678],
                'occupancy_data': [75, 82, 85, 88, 90, 95],
                'guest_satisfaction': 4.5,
                'popular_packages': [
                    {'name': 'Romantic Package', 'bookings': 45},
                    {'name': 'Family Package', 'bookings': 38},
                    {'name': 'Business Package', 'bookings': 25},
                ]
            }
        }
        return render(request, 'dashboard/analytics.html', context)
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def manage_rooms(request):
    try:
        resort = Resort.objects.get(user=request.user)
        return render(request, 'dashboard/rooms.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def manage_guests(request):
    try:
        resort = Resort.objects.get(user=request.user)
        return render(request, 'dashboard/guests.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def manage_reviews(request):
    try:
        resort = Resort.objects.get(user=request.user)
        return render(request, 'dashboard/reviews.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def booking_calendar(request):
    try:
        resort = Resort.objects.get(user=request.user)
        return render(request, 'dashboard/calendar.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def manage_packages(request):
    try:
        resort = Resort.objects.get(user=request.user)
        return render(request, 'dashboard/packages.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def add_package(request):
    try:
        resort = Resort.objects.get(user=request.user)
        if request.method == 'POST':
            # Add package creation logic here
            messages.success(request, 'Package created successfully!')
            return redirect('manage_packages')
        return render(request, 'dashboard/add_package.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def edit_package(request, package_id):
    try:
        resort = Resort.objects.get(user=request.user)
        # Add package editing logic here
        return render(request, 'dashboard/edit_package.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def delete_package(request, package_id):
    try:
        resort = Resort.objects.get(user=request.user)
        # Add package deletion logic here
        messages.success(request, 'Package deleted successfully!')
        return redirect('manage_packages')
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def manage_gallery(request):
    try:
        resort = Resort.objects.get(user=request.user)
        resort_images = resort.images.all()
        return render(request, 'dashboard/gallery.html', {
            'resort': resort,
            'resort_images': resort_images
        })
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def upload_images(request):
    try:
        resort = Resort.objects.get(user=request.user)
        if request.method == 'POST':
            images = request.FILES.getlist('resort_images')
            success_count = 0
            error_count = 0
            
            for image in images:
                try:
                    if image.size > 5 * 1024 * 1024:  # 5MB limit
                        error_count += 1
                        continue
                        
                    ResortImage.objects.create(
                        resort=resort,
                        image=image,
                        is_primary=not resort.images.exists()
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
            
            if success_count > 0:
                messages.success(request, f'{success_count} images uploaded successfully!')
            if error_count > 0:
                messages.warning(request, f'{error_count} images failed to upload.')
                
            return redirect('manage_gallery')
            
        return render(request, 'dashboard/upload_images.html', {'resort': resort})
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def delete_image(request, image_id):
    try:
        resort = Resort.objects.get(user=request.user)
        image = get_object_or_404(ResortImage, id=image_id, resort=resort)
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('manage_gallery')
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def set_primary_image(request, image_id):
    try:
        resort = Resort.objects.get(user=request.user)
        image = get_object_or_404(ResortImage, id=image_id, resort=resort)
        
        # Remove primary status from all other images
        resort.images.all().update(is_primary=False)
        
        # Set the selected image as primary
        image.is_primary = True
        image.save()
        
        messages.success(request, 'Primary image updated successfully!')
        return redirect('manage_gallery')
    except Resort.DoesNotExist:
        messages.warning(request, 'Please create your resort profile first.')
        return redirect('add_profile')

@login_required
def list_packages(request):
    """View to list all packages for a resort"""
    try:
        packages = Package.objects.filter(resort=request.user.resort).order_by('-created_at')
        context = {
            'packages': packages,
            'staycation_count': packages.filter(package_type='Staycation').count(),
            'daycation_count': packages.filter(package_type='Daycation').count(),
        }
        return render(request, 'package/list_packages.html', context)
    except Exception as e:
        messages.error(request, f"Error loading packages: {str(e)}")
        return redirect('ResortDashboard')

@login_required
def create_package(request):
    """View to create a new package"""
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                package = form.save(commit=False)
                package.resort = request.user.resort
                package.save()
                messages.success(request, f"Package '{package.package_name}' created successfully!")
                return redirect('list_packages')
            except Exception as e:
                messages.error(request, f"Error creating package: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PackageForm()
    
    return render(request, 'package/create_package.html', {'form': form})

@login_required
def edit_package(request, package_id):
    """View to edit an existing package"""
    package = get_object_or_404(Package, id=package_id, resort=request.user.resort)
    
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            try:
                # Handle image removal
                if request.POST.get('remove_image') and package.image:
                    package.image.delete()
                    package.image = None
                
                package = form.save()
                messages.success(request, f"Package '{package.package_name}' updated successfully!")
                return redirect('list_packages')
            except Exception as e:
                messages.error(request, f"Error updating package: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PackageForm(instance=package)
    
    return render(request, 'package/edit_package.html', {
        'form': form,
        'package': package
    })

@login_required
def delete_package(request, package_id):
    """View to delete a package"""
    if request.method == 'POST':
        package = get_object_or_404(Package, id=package_id, resort=request.user.resort)
        try:
            package_name = package.package_name
            package.delete()
            messages.success(request, f"Package '{package_name}' deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting package: {str(e)}")
    return redirect('list_packages')
