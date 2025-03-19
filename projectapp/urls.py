from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication URLs
    path('accounts/login/', views.user_login, name='user_login'),
    path('accounts/signup/', views.user_signup, name='user_signup'),
    path('accounts/logout/', views.user_logout, name='user_logout'),
    path('accounts/verify-email/<int:user_id>/', views.verify_email, name='verify_email'),
    path('accounts/resend-verification/<int:user_id>/', views.resend_verification, name='resend_verification'),
    path('accounts/forgot-password/', views.forgot_password, name='forgot_password'),
    path('accounts/reset-password/', views.reset_password, name='reset_password'),
    
    # User Dashboard & Profile
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/add/', views.add_profile, name='add_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('settings/', views.settings_view, name='settings'),
    
    # Resort Management
    path('resort/', views.resortindex, name='resortindex'),
    path('resort/dashboard/', views.ResortDashboard, name='ResortDashboard'),
    path('resort/facilities/', views.manage_facilities, name='manage_facilities'),
    
    # Dashboard Features
    path('resort/bookings/', views.manage_bookings, name='manage_bookings'),
    path('resort/analytics/', views.resort_analytics, name='resort_analytics'),
    path('resort/rooms/', views.manage_rooms, name='manage_rooms'),
    path('resort/rooms/add/', views.add_room, name='add_room'),
    path('resort/rooms/<int:room_id>/edit/', views.edit_room, name='edit_room'),
    path('resort/rooms/<int:room_id>/update/', views.update_room, name='update_room'),
    path('resort/rooms/<int:room_id>/delete/', views.delete_room, name='delete_room'),
    path('resort/rooms/<int:room_id>/mark-cleaned/', views.mark_room_cleaned, name='mark_room_cleaned'),
    path('resort/rooms/<int:room_id>/schedule-maintenance/', views.schedule_maintenance, name='schedule_maintenance'),
    path('resort/rooms/<int:room_id>/details/', views.room_details, name='room_details'),
    path('resort/guests/', views.manage_guests, name='manage_guests'),
    path('resort/reviews/', views.manage_reviews, name='manage_reviews'),
    path('resort/calendar/', views.booking_calendar, name='booking_calendar'),
    
    # Package Management
    path('packages/', views.list_packages, name='list_packages'),
    path('packages/create/', views.create_package, name='create_package'),
    path('packages/<int:package_id>/edit/', views.edit_package, name='edit_package'),
    path('packages/<int:package_id>/delete/', views.delete_package, name='delete_package'),
    
    # Gallery Management
    path('resort/gallery/', views.manage_gallery, name='manage_gallery'),
    path('resort/gallery/upload/', views.upload_images, name='upload_images'),
    path('resort/gallery/<int:image_id>/delete/', views.delete_image, name='delete_image'),
    path('resort/gallery/<int:image_id>/set-primary/', views.set_primary_image, name='set_primary_image'),
    
    # Guest Features
    path('guest/', views.guestindex, name='guestindex'),
    path('rooms/', views.rooms, name='rooms'),
    path('rooms/<int:room_id>/', views.rooms_single, name='rooms_single'),
    path('restaurant/', views.restaurants, name='restaurants'),
    
    # Blog
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_single, name='blog_single'),

    path('guest/signup/', views.guest_signup, name='guest_signup'),
    path('guest/login/', views.guest_login, name='guest_login'),
    path('guest/logout/', views.guest_logout, name='guest_logout'),

    path('guest/profile/', views.guest_profile_view, name='guest_profile_view'),
    path('guest/profile/update/', views.guest_update_profile, name='guest_update_profile'),
    path('guest/profile/change-password/', views.guest_change_password, name='guest_change_password'),
    path('guest/profile/preferences/', views.guest_update_preferences, name='guest_update_preferences'),

    path('explore/', views.explore_page, name='explore_page'),
    path('explore/filter/', views.explore_filter, name='explore_filter'),
    path('explore/sort/<str:sort_by>/', views.explore_sort, name='explore_sort'),

    # Resort Details
    path('resort/<int:resort_id>/', views.resort_detail, name='resort_detail'),
    path('resort/<int:resort_id>/reviews/', views.resort_reviews, name='resort_reviews'),
    path('resort/<int:resort_id>/book/', views.resort_booking, name='resort_booking'),

    # Package Details & Booking
    path('package/<int:package_id>/', views.package_detail, name='package_detail'),
    path('package/<int:package_id>/reviews/', views.package_reviews, name='package_reviews'),
    path('package/<int:package_id>/book/', views.package_booking, name='package_booking'),

    # Payment Processing
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('booking/<int:booking_id>/confirmation/', views.booking_confirmation, name='booking_confirmation'),
    path('booking/verify-qr/', views.verify_booking_qr, name='verify_booking_qr'),

    # Room Details, Reviews & Booking
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('room/<int:room_id>/reviews/', views.room_reviews, name='room_reviews'),
    path('room/<int:room_id>/book/', views.room_booking, name='room_booking'),
    path('room/<int:room_id>/availability/', views.room_availability, name='room_availability'),

    # Booking Process URLs
    path('booking/start/<int:resort_id>/', views.start_booking, name='start_booking'),
    path('booking/guest-details/<int:resort_id>/', views.guest_details, name='guest_details'),
    path('booking/preferences/<int:resort_id>/', views.booking_preferences, name='booking_preferences'),
    path('booking/payment/<int:resort_id>/', views.booking_payment, name='booking_payment'),
    path('booking/payment/process/', views.process_payment, name='process_payment'),
    path('booking/payment/callback/', views.payment_callback, name='payment_callback'),
    path('check-availability/', views.check_availability, name='check_availability'),

]
