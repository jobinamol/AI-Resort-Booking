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
    path('resort/guests/', views.manage_guests, name='manage_guests'),
    path('resort/reviews/', views.manage_reviews, name='manage_reviews'),
    path('resort/calendar/', views.booking_calendar, name='booking_calendar'),
    
    # Package Management
    path('resort/packages/', views.manage_packages, name='manage_packages'),
    path('resort/packages/add/', views.add_package, name='add_package'),
    path('resort/packages/<int:package_id>/edit/', views.edit_package, name='edit_package'),
    path('resort/packages/<int:package_id>/delete/', views.delete_package, name='delete_package'),
    
    # Gallery Management
    path('resort/gallery/', views.manage_gallery, name='manage_gallery'),
    path('resort/gallery/upload/', views.upload_images, name='upload_images'),
    path('resort/gallery/<int:image_id>/delete/', views.delete_image, name='delete_image'),
    path('resort/gallery/<int:image_id>/set-primary/', views.set_primary_image, name='set_primary_image'),
    
    # Guest Features
    path('guest/', views.guestindex, name='guestindex'),
    path('rooms/', views.rooms, name='rooms'),
    path('restaurant/', views.restaurants, name='restaurants'),
    
    # Blog
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_single, name='blog_single'),
]
